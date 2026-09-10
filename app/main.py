from fastapi import FastAPI, Request, HTTPException, Query, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from typing import Optional, List
import sqlite3
import json
import os

from app.database import get_db_connection, DB_PATH, get_setting, set_setting
from app.models import (
    InquiryCreate, StockAlertCreate, InventoryUpdate, InquiryStatusUpdate, 
    AdminLoginRequest, SheetsConfigRequest, SheetsSyncRequest
)
from app.auth import (
    authenticate_user, create_session, get_user_from_session,
    delete_session, SESSION_COOKIE_NAME
)
from app.sheets_sync import (
    sync_from_google_sheet_url, generate_sample_csv
)
from app.google_sheets_service import (
    store_inquiry_in_google_sheet, CSV_FILE_PATH, get_google_apps_script_template
)

app = FastAPI(title="ScoutMyVehicle - Multi-Brand Showroom Stock Network", version="1.0.0")

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

STATIC_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Helper to fetch dict rows
def dict_rows(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def get_authenticated_user(request: Request) -> Optional[dict]:
    token = request.cookies.get(SESSION_COOKIE_NAME)
    return get_user_from_session(token)

# ----------------- PAGE ROUTES -----------------

@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get dealerships
    cursor.execute("SELECT * FROM dealerships ORDER BY city ASC, rating DESC;")
    dealerships = dict_rows(cursor)

    # Get distinct brands
    cursor.execute("SELECT DISTINCT make FROM cars ORDER BY make ASC;")
    brands = [r[0] for r in cursor.fetchall()]

    # Get cars with price formatting
    cursor.execute("SELECT * FROM cars ORDER BY popular_choice DESC, id ASC;")
    cars = dict_rows(cursor)

    # Get summary metrics
    cursor.execute("""
        SELECT 
            SUM(CASE WHEN status = 'IN_STOCK' THEN units_available ELSE 0 END) as ready_stock_count,
            SUM(CASE WHEN status = 'IN_TRANSIT' THEN units_available ELSE 0 END) as in_transit_count,
            COUNT(DISTINCT dealership_id) as dealers_count,
            COUNT(DISTINCT car_id) as models_count
        FROM inventory i
        JOIN variants v ON i.variant_id = v.id;
    """)
    stats = dict(cursor.fetchone())

    conn.close()

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "dealerships": dealerships,
            "brands": brands,
            "cars": cars,
            "stats": stats
        }
    )

@app.get("/admin")
async def admin_redirect(request: Request):
    return RedirectResponse(url="/dealer", status_code=302)

@app.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page(request: Request, next: Optional[str] = "/dealer"):
    current_user = get_authenticated_user(request)
    if current_user:
        return RedirectResponse(url=next or "/dealer", status_code=302)
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"next_url": next or "/dealer"}
    )

@app.post("/api/admin/login")
async def api_admin_login(data: AdminLoginRequest):
    user = authenticate_user(data.username, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password. Please try again.")

    token = create_session(user["id"])

    target_url = data.next_url or "/dealer"
    if user["dealership_id"] and "/dealer" in target_url and "dealership_id" not in target_url:
        target_url = f"/dealer?dealership_id={user['dealership_id']}"

    response = JSONResponse(content={
        "success": True,
        "message": f"Welcome back, {user['name']}!",
        "user": {
            "id": user["id"],
            "username": user["username"],
            "name": user["name"],
            "role": user["role"]
        },
        "redirect_url": target_url
    })

    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="lax",
        max_age=7 * 24 * 3600
    )
    return response

@app.get("/admin/logout")
async def admin_logout(request: Request):
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if token:
        delete_session(token)
    response = RedirectResponse(url="/admin/login", status_code=302)
    response.delete_cookie(SESSION_COOKIE_NAME)
    return response

@app.get("/dealer", response_class=HTMLResponse)
async def dealer_portal(request: Request, dealership_id: Optional[int] = None):
    current_user = get_authenticated_user(request)
    if not current_user:
        return RedirectResponse(url="/admin/login?next=/dealer", status_code=302)

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch all dealerships
    cursor.execute("SELECT * FROM dealerships ORDER BY city ASC, name ASC;")
    dealerships = dict_rows(cursor)

    # Default to user's assigned branch if not explicitly specified
    if not dealership_id and current_user.get("dealership_id"):
        current_dealer_id = current_user["dealership_id"]
    else:
        current_dealer_id = dealership_id if dealership_id else (dealerships[0]["id"] if dealerships else 1)

    # Fetch selected dealer info
    cursor.execute("SELECT * FROM dealerships WHERE id = ?;", (current_dealer_id,))
    current_dealer = dict(cursor.fetchone()) if cursor.rowcount != 0 else dealerships[0]

    conn.close()

    return templates.TemplateResponse(
        request=request,
        name="dealer_portal.html",
        context={
            "dealerships": dealerships,
            "current_dealer": current_dealer,
            "current_user": current_user
        }
    )

# ----------------- REST API ROUTES -----------------

@app.get("/api/brands")
async def get_brands():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT make FROM cars ORDER BY make ASC;")
    brands = [r[0] for r in cursor.fetchall()]
    conn.close()
    return brands

@app.get("/api/dealerships")
async def get_dealerships(city: Optional[str] = None, brand: Optional[str] = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM dealerships WHERE 1=1"
    params = []
    if city and city.lower() not in ["all", "any", "others"]:
        query += " AND LOWER(city) = LOWER(?)"
        params.append(city)
    if brand and brand.lower() not in ["all", "any"]:
        query += " AND LOWER(brand) = LOWER(?)"
        params.append(brand)
    query += " ORDER BY city ASC, rating DESC;"
    cursor.execute(query, params)
    rows = dict_rows(cursor)
    conn.close()
    return rows

@app.get("/api/cars")
async def get_cars(brand: Optional[str] = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM cars WHERE 1=1"
    params = []
    if brand and brand.lower() not in ["all", "any"]:
        query += " AND LOWER(make) = LOWER(?)"
        params.append(brand)
    query += " ORDER BY popular_choice DESC, id ASC;"
    cursor.execute(query, params)
    cars = dict_rows(cursor)
    
    # Attach variant, stock stats, fuel types, transmissions, colors, and dealership info to each car
    for car in cars:
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT v.id) as variants_count,
                SUM(CASE WHEN i.status = 'IN_STOCK' THEN i.units_available ELSE 0 END) as ready_units,
                SUM(CASE WHEN i.status = 'IN_TRANSIT' THEN i.units_available ELSE 0 END) as transit_units,
                MIN(CASE WHEN i.status = 'WAITLIST' THEN i.waiting_period_weeks ELSE NULL END) as min_wait_weeks
            FROM variants v
            LEFT JOIN inventory i ON v.id = i.variant_id
            WHERE v.car_id = ?;
        """, (car["id"],))
        stats = dict(cursor.fetchone())
        car["stats"] = stats

        cursor.execute("""
            SELECT id, name, fuel_type, transmission, ex_showroom_price, drivetrain, seating, engine_spec, key_features
            FROM variants
            WHERE car_id = ?
            ORDER BY ex_showroom_price ASC, id ASC;
        """, (car["id"],))
        variants = dict_rows(cursor)
        car["variants"] = variants
        car["fuel_types_list"] = sorted(list(set(v["fuel_type"] for v in variants if v.get("fuel_type"))))
        car["transmissions_list"] = sorted(list(set(v["transmission"] for v in variants if v.get("transmission"))))

        cursor.execute("""
            SELECT DISTINCT i.colors_available
            FROM inventory i
            JOIN variants v ON i.variant_id = v.id
            WHERE v.car_id = ?;
        """, (car["id"],))
        color_set = set()
        for row in cursor.fetchall():
            if row[0]:
                for c in row[0].split(","):
                    c_clean = c.strip()
                    if c_clean:
                        color_set.add(c_clean)
        if not color_set:
            color_set = {"Pearl White", "Silver", "Metallic Grey", "Black", "Red"}
        car["colors"] = sorted(list(color_set))

        cursor.execute("""
            SELECT d.id FROM dealerships d
            WHERE LOWER(d.brand) = LOWER(?) OR LOWER(d.name) LIKE '%' || LOWER(?) || '%'
            LIMIT 1;
        """, (car["make"], car["make"]))
        dealer_row = cursor.fetchone()
        car["dealership_id"] = dealer_row[0] if dealer_row else 1

    conn.close()
    return cars

@app.get("/api/variants")
async def get_variants(model: Optional[str] = None, brand: Optional[str] = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT DISTINCT v.name 
        FROM variants v
        JOIN cars c ON v.car_id = c.id
        WHERE 1=1
    """
    params = []
    if model and model.lower() not in ["all", "any"]:
        query += " AND (LOWER(c.model) = LOWER(?) OR c.slug = ? OR LOWER(c.model) LIKE LOWER(?) OR LOWER(?) LIKE '%' || LOWER(c.model) || '%')"
        params.extend([model, model, f"%{model}%", model])
    if brand and brand.lower() not in ["all", "any"]:
        query += " AND LOWER(c.make) = LOWER(?)"
        params.append(brand)
    query += " ORDER BY v.name ASC;"
    cursor.execute(query, params)
    rows = [r[0] for r in cursor.fetchall()]
    conn.close()
    return rows

@app.get("/api/colors")
async def get_colors(brand: Optional[str] = None, model: Optional[str] = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT DISTINCT i.colors_available
        FROM inventory i
        JOIN variants v ON i.variant_id = v.id
        JOIN cars c ON v.car_id = c.id
        WHERE i.status = 'IN_STOCK' AND i.units_available > 0
    """
    params = []
    if brand and brand.lower() not in ["all", "any"]:
        query += " AND LOWER(c.make) = LOWER(?)"
        params.append(brand)
    if model and model.lower() not in ["all", "any"]:
        query += " AND (LOWER(c.model) = LOWER(?) OR c.slug = ? OR LOWER(c.model) LIKE LOWER(?) OR LOWER(?) LIKE '%' || LOWER(c.model) || '%')"
        params.extend([model, model, f"%{model}%", model])
    cursor.execute(query, params)
    raw_colors = [r[0] for r in cursor.fetchall() if r[0]]
    color_set = set()
    for row in raw_colors:
        for c in row.split(","):
            c_clean = c.strip()
            if c_clean:
                color_set.add(c_clean)
    conn.close()
    return sorted(list(color_set))

@app.get("/api/inventory")
async def get_inventory(
    city: Optional[str] = None,
    customer_location: Optional[str] = None,
    brand: Optional[str] = None,
    car_slug: Optional[str] = None,
    model: Optional[str] = None,
    variant: Optional[str] = None,
    color: Optional[str] = None,
    status: Optional[str] = None,
    transmission: Optional[str] = None,
    fuel_type: Optional[str] = None,
    search: Optional[str] = None,
    max_price: Optional[float] = None
):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT 
            i.id as inventory_id,
            i.status,
            i.units_available,
            i.waiting_period_weeks,
            i.colors_available,
            i.test_drive_available,
            i.promo_note,
            i.updated_at,
            d.id as dealership_id,
            d.brand as dealer_brand,
            d.name as dealer_name,
            d.city as dealer_city,
            d.rto_code,
            d.address as dealer_address,
            d.phone as dealer_phone,
            d.whatsapp as dealer_whatsapp,
            d.manager_name as dealer_manager,
            d.rating as dealer_rating,
            c.id as car_id,
            c.make as car_brand,
            c.model as car_model,
            c.slug as car_slug,
            c.category as car_category,
            c.hero_image,
            v.id as variant_id,
            v.name as variant_name,
            v.fuel_type,
            v.transmission,
            v.drivetrain,
            v.seating,
            v.engine_spec,
            v.ex_showroom_price,
            v.key_features
        FROM inventory i
        JOIN dealerships d ON i.dealership_id = d.id
        JOIN variants v ON i.variant_id = v.id
        JOIN cars c ON v.car_id = c.id
        WHERE 1=1
    """
    params = []

    # Filter out unavailable cars by default (strictly available stock)
    if status and status.lower() not in ["all", "any"]:
        query += " AND i.status = ?"
        params.append(status.upper())
    else:
        query += " AND i.status = 'IN_STOCK' AND i.units_available > 0"

    target_city = customer_location if (customer_location and customer_location.lower() not in ["all", "any", "others"]) else city
    if target_city and target_city.lower() not in ["all", "any", "others"]:
        query += " AND LOWER(d.city) = LOWER(?)"
        params.append(target_city)

    if brand and brand.lower() not in ["all", "any"]:
        query += " AND (LOWER(c.make) = LOWER(?) OR LOWER(d.brand) = LOWER(?))"
        params.extend([brand, brand])

    if model and model.lower() not in ["all", "any"]:
        query += " AND (LOWER(c.model) = LOWER(?) OR c.slug = ? OR LOWER(c.model) LIKE LOWER(?) OR LOWER(?) LIKE '%' || LOWER(c.model) || '%')"
        params.extend([model, model, f"%{model}%", model])
    elif car_slug and car_slug.lower() not in ["all", "any"]:
        query += " AND c.slug = ?"
        params.append(car_slug)

    if variant and variant.lower() not in ["all", "any"]:
        query += " AND LOWER(v.name) LIKE LOWER(?)"
        params.append(f"%{variant}%")

    if color and color.lower() not in ["all", "any"]:
        query += " AND LOWER(i.colors_available) LIKE LOWER(?)"
        params.append(f"%{color}%")

    if transmission and transmission.lower() not in ["all", "any"]:
        t_low = transmission.lower().strip()
        if t_low in ["manual", "mt"]:
            query += " AND (LOWER(v.transmission) LIKE '%manual%' OR LOWER(v.transmission) = 'mt' OR LOWER(v.transmission) LIKE '%(mt)%') AND LOWER(v.transmission) NOT LIKE '%amt%' AND LOWER(v.transmission) NOT LIKE '%imt%'"
        elif t_low in ["automatic", "at"]:
            query += " AND (LOWER(v.transmission) LIKE '%automatic%' OR LOWER(v.transmission) = 'at' OR LOWER(v.transmission) LIKE '%(at)%') AND LOWER(v.transmission) NOT LIKE '%amt%'"
        elif t_low in ["amt"]:
            query += " AND LOWER(v.transmission) LIKE '%amt%'"
        elif t_low in ["dct", "dca", "dsg"]:
            query += " AND (LOWER(v.transmission) LIKE '%dct%' OR LOWER(v.transmission) LIKE '%dca%' OR LOWER(v.transmission) LIKE '%dsg%')"
        elif t_low in ["cvt", "ivt"]:
            query += " AND (LOWER(v.transmission) LIKE '%cvt%' OR LOWER(v.transmission) LIKE '%ivt%') AND LOWER(v.transmission) NOT LIKE '%e-cvt%'"
        elif t_low in ["e-cvt", "ecvt"]:
            query += " AND (LOWER(v.transmission) LIKE '%e-cvt%' OR LOWER(v.transmission) LIKE '%ecvt%')"
        elif t_low in ["imt"]:
            query += " AND LOWER(v.transmission) LIKE '%imt%'"
        else:
            query += " AND LOWER(v.transmission) LIKE LOWER(?)"
            params.append(f"%{transmission}%")

    if fuel_type and fuel_type.lower() not in ["all", "any"]:
        f_low = fuel_type.lower().strip()
        if f_low == "petrol":
            query += " AND LOWER(v.fuel_type) LIKE '%petrol%'"
        else:
            query += " AND LOWER(v.fuel_type) LIKE LOWER(?)"
            params.append(f"%{fuel_type}%")

    if max_price and max_price > 0:
        price_val = int(max_price * 100000) if max_price <= 100 else int(max_price)
        query += " AND v.ex_showroom_price <= ?"
        params.append(price_val)

    if search and search.strip():
        search_param = f"%{search.strip()}%"
        query += """ AND (
            LOWER(c.make) LIKE LOWER(?) OR
            LOWER(c.model) LIKE LOWER(?) OR 
            LOWER(v.name) LIKE LOWER(?) OR 
            LOWER(i.colors_available) LIKE LOWER(?) OR 
            LOWER(d.name) LIKE LOWER(?) OR 
            LOWER(d.city) LIKE LOWER(?)
        )"""
        params.extend([search_param, search_param, search_param, search_param, search_param, search_param])

    query += " ORDER BY CASE i.status WHEN 'IN_STOCK' THEN 1 WHEN 'IN_TRANSIT' THEN 2 ELSE 3 END, i.id ASC;"

    cursor.execute(query, params)
    rows = dict_rows(cursor)
    conn.close()
    return rows

@app.get("/api/compare/{car_slug}")
async def compare_car_dealerships(car_slug: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get car (support both thar-roxx and mahindra-thar-roxx)
    clean_slug = car_slug if car_slug.startswith("mahindra-") else f"mahindra-{car_slug}"
    short_slug = car_slug.replace("mahindra-", "")
    cursor.execute("SELECT * FROM cars WHERE slug = ? OR slug = ? OR slug = ?;", (car_slug, clean_slug, short_slug))
    car = cursor.fetchone()
    if not car:
        conn.close()
        raise HTTPException(status_code=404, detail="Car not found")
    car = dict(car)

    # Fetch dealerships
    cursor.execute("SELECT * FROM dealerships ORDER BY city ASC, rating DESC;")
    dealerships = dict_rows(cursor)

    # For each dealership, fetch inventory for this car
    dealership_comparison = []
    for d in dealerships:
        cursor.execute("""
            SELECT 
                i.id as inventory_id,
                i.status,
                i.units_available,
                i.waiting_period_weeks,
                i.colors_available,
                i.test_drive_available,
                i.promo_note,
                v.name as variant_name,
                v.fuel_type,
                v.transmission,
                v.ex_showroom_price
            FROM inventory i
            JOIN variants v ON i.variant_id = v.id
            WHERE i.dealership_id = ? AND v.car_id = ?
            ORDER BY CASE i.status WHEN 'IN_STOCK' THEN 1 WHEN 'IN_TRANSIT' THEN 2 ELSE 3 END;
        """, (d["id"], car["id"]))
        inventory_items = dict_rows(cursor)

        has_ready_stock = any(item["status"] == "IN_STOCK" and item["units_available"] > 0 for item in inventory_items)
        has_in_transit = any(item["status"] == "IN_TRANSIT" for item in inventory_items)
        test_drive_ready = any(item["test_drive_available"] == 1 for item in inventory_items)

        dealership_comparison.append({
            "dealership": d,
            "has_ready_stock": has_ready_stock,
            "has_in_transit": has_in_transit,
            "test_drive_ready": test_drive_ready,
            "stock_count": sum(item["units_available"] for item in inventory_items),
            "inventory": inventory_items
        })

    conn.close()
    return {
        "car": car,
        "dealerships": dealership_comparison
    }

@app.post("/api/inquiries")
async def create_inquiry(inquiry: InquiryCreate):
    conn = get_db_connection()
    cursor = conn.cursor()

    dealer_id = inquiry.dealership_id if inquiry.dealership_id else 1
    cursor.execute("""
        INSERT INTO inquiries (
            dealership_id, car_id, variant_id, customer_name, customer_phone, customer_email, customer_city,
            inquiry_type, preferred_date, preferred_time, buying_timeline, finance_required,
            exchange_required, exchange_car_details, notes, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'NEW');
    """, (
        dealer_id, inquiry.car_id, inquiry.variant_id,
        inquiry.customer_name, inquiry.customer_phone, inquiry.customer_email, inquiry.customer_city,
        inquiry.inquiry_type, inquiry.preferred_date, inquiry.preferred_time,
        inquiry.buying_timeline, inquiry.finance_required, inquiry.exchange_required,
        inquiry.exchange_car_details, inquiry.notes
    ))
    inquiry_id = cursor.lastrowid
    conn.commit()

    # Fetch dealer details for response
    cursor.execute("SELECT name, phone, whatsapp, city FROM dealerships WHERE id = ?;", (dealer_id,))
    dealer_row = cursor.fetchone()
    dealer = dict(dealer_row) if dealer_row else {"name": "Authorized Showroom", "phone": "+91 5946 220 188", "whatsapp": "919837012345", "city": "Uttarakhand"}

    # Fetch vehicle & variant details for WhatsApp & Google Sheet
    car_name = "Selected Model"
    variant_name = "Standard"
    fuel_name = "N/A"
    transmission_name = "N/A"
    price_val = "N/A"
    if inquiry.car_id:
        cursor.execute("SELECT make, model FROM cars WHERE id = ?;", (inquiry.car_id,))
        c_row = cursor.fetchone()
        if c_row:
            car_name = f"{c_row[0]} {c_row[1]}"
    if inquiry.variant_id:
        cursor.execute("SELECT name, fuel_type, transmission, ex_showroom_price FROM variants WHERE id = ?;", (inquiry.variant_id,))
        v_row = cursor.fetchone()
        if v_row:
            variant_name = v_row[0]
            fuel_name = v_row[1]
            transmission_name = v_row[2]
            price_val = f"₹ {v_row[3]:,}" if v_row[3] else "N/A"

    # Extract preferred bank if specified in notes
    preferred_bank = "N/A"
    if inquiry.notes:
        if "Preferred Bank:" in inquiry.notes:
            try:
                preferred_bank = inquiry.notes.split("Preferred Bank:")[1].split(")")[0].split("|")[0].strip()
            except Exception:
                pass
        elif "Finance:" in inquiry.notes and "(" in inquiry.notes:
            try:
                candidate = inquiry.notes.split("(")[1].split(")")[0].strip()
                if any(b in candidate for b in ["SBI", "PNB", "HDFC", "Chola"]):
                    preferred_bank = candidate
            except Exception:
                pass

    # WhatsApp Direct Message to +919275251003
    whatsapp_target_number = "+919275251003"
    wa_digits = "919275251003"
    whatsapp_msg = (
        f"🚗 *New Vehicle Enquiry - ScoutMyVehicle*\n"
        f"----------------------------------------\n"
        f"*Customer Information:*\n"
        f"• Name: {inquiry.customer_name}\n"
        f"• Phone: {inquiry.customer_phone}\n"
        f"• Email: {inquiry.customer_email or 'N/A'}\n"
        f"• Location: {inquiry.customer_city or 'Not Specified'}\n\n"
        f"*Vehicle Selected:*\n"
        f"• Model: {car_name}\n"
        f"• Variant: {variant_name}\n"
        f"• Fuel: {fuel_name}\n"
        f"• Transmission: {transmission_name}\n\n"
        f"*Purchase Preferences:*\n"
        f"• Timeline: {inquiry.buying_timeline or 'N/A'}\n"
        f"• Finance: {inquiry.finance_required or 'No'}\n"
        f"• Preferred Bank: {preferred_bank}\n"
        f"• Exchange: {'Yes - ' + str(inquiry.exchange_car_details) if inquiry.exchange_required else 'No'}\n"
        f"----------------------------------------"
    )
    import urllib.parse
    whatsapp_url = f"https://api.whatsapp.com/send?phone={wa_digits}&text={urllib.parse.quote(whatsapp_msg)}"

    # Store inquiry in Google Sheet (Local CSV & Webhook if configured)
    inquiry_record = {
        "inquiry_id": inquiry_id,
        "customer_name": inquiry.customer_name,
        "customer_phone": inquiry.customer_phone,
        "customer_email": inquiry.customer_email,
        "customer_city": inquiry.customer_city,
        "car_model": car_name,
        "variant_name": variant_name,
        "fuel_type": fuel_name,
        "transmission": transmission_name,
        "price": price_val,
        "buying_timeline": inquiry.buying_timeline,
        "finance_required": inquiry.finance_required,
        "preferred_bank": preferred_bank,
        "exchange_required": inquiry.exchange_required,
        "exchange_car_details": inquiry.exchange_car_details,
        "notes": inquiry.notes
    }
    webhook_url = get_setting("google_sheet_inquiries_webhook", "") or os.getenv("GOOGLE_SHEET_INQUIRIES_WEBHOOK", "")
    sheet_result = store_inquiry_in_google_sheet(inquiry_record, webhook_url=webhook_url)

    conn.close()

    return {
        "success": True,
        "inquiry_id": inquiry_id,
        "message": f"Inquiry registered with {dealer['name']} ({dealer['city']})!",
        "dealer": dealer,
        "whatsapp_number": whatsapp_target_number,
        "whatsapp_url": whatsapp_url,
        "google_sheet_stored": sheet_result.get("stored_in_csv", True)
    }

@app.get("/api/inquiries/export.csv")
async def export_inquiries_csv():
    """Exports all stored customer inquiries in Google Sheets compatible CSV format."""
    if os.path.exists(CSV_FILE_PATH):
        return FileResponse(
            path=CSV_FILE_PATH,
            filename="scoutmyvehicle_inquiries.csv",
            media_type="text/csv"
        )
    return Response(content="Timestamp,Inquiry ID,Customer Name,Customer Phone\n", media_type="text/csv")

@app.get("/api/admin/sheets/inquiries-config")
async def get_inquiries_sheets_config(request: Request):
    current_user = get_authenticated_user(request)
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return {
        "webhook_url": get_setting("google_sheet_inquiries_webhook", ""),
        "csv_export_url": "/api/inquiries/export.csv",
        "script_template": get_google_apps_script_template()
    }

@app.post("/api/admin/sheets/inquiries-config")
async def save_inquiries_sheets_config(data: dict, request: Request):
    current_user = get_authenticated_user(request)
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    url = data.get("webhook_url", "").strip()
    set_setting("google_sheet_inquiries_webhook", url)
    return {"success": True, "message": "Google Sheet inquiry webhook URL saved"}

@app.post("/api/stock-alerts")
async def create_stock_alert(alert: StockAlertCreate):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO stock_alerts (customer_name, customer_phone, car_id, preferred_city, preferred_color)
        VALUES (?, ?, ?, ?, ?);
    """, (alert.customer_name, alert.customer_phone, alert.car_id, alert.preferred_city, alert.preferred_color))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": f"Stock alert registered! You will receive an instant SMS/WhatsApp when matching stock arrives in {alert.preferred_city}."
    }

# ----------------- DEALER PORTAL API -----------------

@app.get("/api/dealer/inventory/{dealership_id}")
async def get_dealer_inventory(dealership_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            i.id as inventory_id,
            i.status,
            i.units_available,
            i.waiting_period_weeks,
            i.colors_available,
            i.test_drive_available,
            i.promo_note,
            i.updated_at,
            c.model as car_model,
            c.slug as car_slug,
            v.id as variant_id,
            v.name as variant_name,
            v.fuel_type,
            v.transmission,
            v.ex_showroom_price
        FROM inventory i
        JOIN variants v ON i.variant_id = v.id
        JOIN cars c ON v.car_id = c.id
        WHERE i.dealership_id = ?
        ORDER BY c.popular_choice DESC, v.ex_showroom_price DESC;
    """, (dealership_id,))

    rows = dict_rows(cursor)
    conn.close()
    return rows

@app.post("/api/dealer/inventory/update")
async def update_dealer_inventory(update: InventoryUpdate):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE inventory
        SET status = ?,
            units_available = ?,
            waiting_period_weeks = ?,
            colors_available = ?,
            test_drive_available = ?,
            promo_note = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?;
    """, (
        update.status,
        update.units_available,
        update.waiting_period_weeks,
        update.colors_available,
        update.test_drive_available,
        update.promo_note,
        update.inventory_id
    ))

    conn.commit()
    conn.close()

    return {"success": True, "message": "Inventory updated successfully"}

@app.get("/api/dealer/inquiries/{dealership_id}")
async def get_dealer_inquiries(dealership_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            inq.*,
            c.model as car_model,
            v.name as variant_name
        FROM inquiries inq
        LEFT JOIN cars c ON inq.car_id = c.id
        LEFT JOIN variants v ON inq.variant_id = v.id
        WHERE inq.dealership_id = ?
        ORDER BY inq.created_at DESC;
    """, (dealership_id,))

    rows = dict_rows(cursor)
    conn.close()
    return rows

@app.post("/api/dealer/inquiry/status")
async def update_inquiry_status(update: InquiryStatusUpdate):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE inquiries
        SET status = ?
        WHERE id = ?;
    """, (update.status, update.inquiry_id))

    conn.commit()
    conn.close()

    return {"success": True, "message": f"Inquiry status updated to {update.status}"}

@app.get("/api/price-estimate")
async def get_price_estimate(variant_id: int, rto_city: str = "Haldwani"):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT v.*, c.model as car_model
        FROM variants v
        JOIN cars c ON v.car_id = c.id
        WHERE v.id = ?;
    """, (variant_id,))
    variant = cursor.fetchone()
    conn.close()

    if not variant:
        raise HTTPException(status_code=404, detail="Variant not found")
    variant = dict(variant)

    ex_showroom = variant["ex_showroom_price"]

    # Uttarakhand RTO tax calculation (roughly 8% - 10% depending on engine/price tier)
    if ex_showroom < 1000000:
        rto_rate = 0.08
    else:
        rto_rate = 0.10
    
    rto_tax = int(ex_showroom * rto_rate)
    # Comprehensive 3yr TP + 1yr OD Insurance approx 3.5%
    insurance = int(ex_showroom * 0.038) + 12000
    tcs = int(ex_showroom * 0.01) if ex_showroom > 1000000 else 0
    fastag_reg = 2500
    total_on_road = ex_showroom + rto_tax + insurance + tcs + fastag_reg

    return {
        "variant": variant,
        "rto_city": rto_city,
        "rto_code": "UK-04 (Haldwani)" if "haldwani" in rto_city.lower() else "UK-06 (Rudrapur)",
        "ex_showroom": ex_showroom,
        "rto_tax": rto_tax,
        "insurance": insurance,
        "tcs": tcs,
        "fastag_registration": fastag_reg,
        "total_on_road": total_on_road
    }

# ----------------- GOOGLE SHEETS SYNC ROUTES -----------------

@app.get("/api/admin/sheets/config")
async def get_sheets_config(request: Request):
    user = get_authenticated_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return {
        "google_sheet_url": get_setting("google_sheet_url", ""),
        "last_sync_time": get_setting("last_sync_time", "Never"),
        "last_sync_status": get_setting("last_sync_status", "No sync performed yet"),
        "last_sync_count": get_setting("last_sync_count", "0")
    }

@app.post("/api/admin/sheets/config")
async def save_sheets_config(config: SheetsConfigRequest, request: Request):
    user = get_authenticated_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    set_setting("google_sheet_url", config.google_sheet_url.strip())
    return {"success": True, "message": "Google Sheet URL saved successfully"}

@app.post("/api/admin/sheets/sync")
async def sync_google_sheets(request: Request, sync_req: Optional[SheetsSyncRequest] = None):
    user = get_authenticated_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")

    url = (sync_req.google_sheet_url if sync_req and sync_req.google_sheet_url else None) or get_setting("google_sheet_url")
    if not url or not url.strip():
        raise HTTPException(status_code=400, detail="No Google Sheet URL provided or saved. Please enter your Google Sheet sharing link.")

    try:
        result = sync_from_google_sheet_url(url.strip())
        return result
    except PermissionError as pe:
        raise HTTPException(status_code=403, detail=str(pe))
    except (ValueError, ConnectionError, RuntimeError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error during sync: {str(e)}")

@app.get("/api/admin/sheets/template.csv")
async def download_sheets_template():
    csv_content = generate_sample_csv()
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=scoutmycar_dealership_stock_template.csv"
        }
    )
