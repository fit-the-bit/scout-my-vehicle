from fastapi import FastAPI, Request, HTTPException, Query, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from typing import Optional, List
import sqlite3
import json

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
    
    # Attach variant and stock stats to each car
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
        query += " AND (LOWER(c.model) = LOWER(?) OR c.slug = ?)"
        params.extend([model, model])
    if brand and brand.lower() not in ["all", "any"]:
        query += " AND LOWER(c.make) = LOWER(?)"
        params.append(brand)
    query += " ORDER BY v.name ASC;"
    cursor.execute(query, params)
    rows = [r[0] for r in cursor.fetchall()]
    conn.close()
    return rows

@app.get("/api/inventory")
async def get_inventory(
    city: Optional[str] = None,
    customer_location: Optional[str] = None,
    brand: Optional[str] = None,
    car_slug: Optional[str] = None,
    model: Optional[str] = None,
    variant: Optional[str] = None,
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

    target_city = customer_location if (customer_location and customer_location.lower() not in ["all", "any", "others"]) else city
    if target_city and target_city.lower() not in ["all", "any", "others"]:
        query += " AND LOWER(d.city) = LOWER(?)"
        params.append(target_city)

    if brand and brand.lower() not in ["all", "any"]:
        query += " AND (LOWER(c.make) = LOWER(?) OR LOWER(d.brand) = LOWER(?))"
        params.extend([brand, brand])

    if model and model.lower() not in ["all", "any"]:
        query += " AND (LOWER(c.model) = LOWER(?) OR c.slug = ?)"
        params.extend([model, model])
    elif car_slug and car_slug.lower() not in ["all", "any"]:
        query += " AND c.slug = ?"
        params.append(car_slug)

    if variant and variant.lower() not in ["all", "any"]:
        query += " AND LOWER(v.name) LIKE LOWER(?)"
        params.append(f"%{variant}%")

    if status and status.lower() not in ["all", "any"]:
        query += " AND i.status = ?"
        params.append(status.upper())

    if transmission and transmission.lower() not in ["all", "any"]:
        query += " AND LOWER(v.transmission) LIKE LOWER(?)"
        params.append(f"%{transmission}%")

    if fuel_type and fuel_type.lower() not in ["all", "any"]:
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

    cursor.execute("""
        INSERT INTO inquiries (
            dealership_id, car_id, variant_id, customer_name, customer_phone, customer_city,
            inquiry_type, preferred_date, preferred_time, buying_timeline, finance_required,
            exchange_required, exchange_car_details, notes, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'NEW');
    """, (
        inquiry.dealership_id, inquiry.car_id, inquiry.variant_id,
        inquiry.customer_name, inquiry.customer_phone, inquiry.customer_city,
        inquiry.inquiry_type, inquiry.preferred_date, inquiry.preferred_time,
        inquiry.buying_timeline, inquiry.finance_required, inquiry.exchange_required,
        inquiry.exchange_car_details, inquiry.notes
    ))
    inquiry_id = cursor.lastrowid
    conn.commit()

    # Fetch dealer details for response (for whatsapp/phone direct connect prompt)
    cursor.execute("SELECT name, phone, whatsapp, city FROM dealerships WHERE id = ?;", (inquiry.dealership_id,))
    dealer_row = cursor.fetchone()
    dealer = dict(dealer_row) if dealer_row else {"name": "Mahindra Showroom", "phone": "+91 5946 220 188", "whatsapp": "919837012345", "city": "Uttarakhand"}

    conn.close()

    return {
        "success": True,
        "inquiry_id": inquiry_id,
        "message": f"Inquiry registered with {dealer['name']} ({dealer['city']})!",
        "dealer": dealer
    }

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
