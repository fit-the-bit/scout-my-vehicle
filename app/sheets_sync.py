import csv
import io
import re
import urllib.request
import urllib.error
from datetime import datetime, timezone
from typing import Optional, List, Dict, Tuple
from app.database import get_db_connection, set_setting, get_setting

# Clean column headers
CSV_HEADERS = [
    "Brand",
    "Dealership",
    "City",
    "Model",
    "Variant",
    "Fuel",
    "Transmission",
    "Status",
    "Units",
    "WaitingWeeks",
    "Colors",
    "PromoNote"
]

def parse_google_sheets_url(url: str) -> str:
    """
    Extracts the Spreadsheet ID and gid from any Google Sheet URL 
    and returns a direct CSV download export URL.
    """
    url = url.strip()
    # Match spreadsheet ID: /spreadsheets/d/([a-zA-Z0-9-_]+)
    match = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", url)
    if not match:
        # If user just pasted the raw ID
        if re.match(r"^[a-zA-Z0-9-_]{20,}$", url):
            sheet_id = url
            gid = "0"
        else:
            raise ValueError("Invalid Google Sheets URL format. Please provide a standard Google Sheets sharing link.")
    else:
        sheet_id = match.group(1)
        # Extract gid if present (e.g. #gid=12345 or ?gid=12345)
        gid_match = re.search(r"[#?&]gid=([0-9]+)", url)
        gid = gid_match.group(1) if gid_match else "0"

    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"

def fetch_sheets_csv(url: str) -> str:
    """
    Fetches raw CSV text from Google Sheets export URL.
    """
    csv_url = parse_google_sheets_url(url)
    req = urllib.request.Request(
        csv_url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ScoutMyCar/1.0"}
    )
    try:
        with urllib.request.urlopen(req, timeout=12) as response:
            content_type = response.headers.get("Content-Type", "")
            data = response.read().decode("utf-8", errors="replace")
            # If Google Sheets returned an HTML login page instead of CSV, it's not public
            if "<html" in data.lower() and "google" in data.lower() and "sign in" in data.lower():
                raise PermissionError("Google Sheet is not publicly accessible. Please set Share settings to 'Anyone with the link can view'.")
            return data
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            raise PermissionError("Access denied. In your Google Sheet, click Share and set General Access to 'Anyone with the link can view'.")
        raise RuntimeError(f"HTTP Error {e.code} while connecting to Google Sheets.")
    except urllib.error.URLError as e:
        raise ConnectionError(f"Network error connecting to Google Sheets: {e.reason}")

def normalize_status(val: str) -> str:
    """Normalizes raw status strings into IN_STOCK, IN_TRANSIT, or WAITLIST."""
    s = (val or "").strip().upper()
    if any(k in s for k in ["IN STOCK", "IN_STOCK", "READY", "AVAILABLE", "YES"]):
        return "IN_STOCK"
    elif any(k in s for k in ["TRANSIT", "ARRIVING", "ON THE WAY"]):
        return "IN_TRANSIT"
    elif any(k in s for k in ["SOLD", "WAIT", "BOOKING", "OUT"]):
        return "WAITLIST"
    return "IN_STOCK"

def parse_csv_records(csv_text: str) -> List[Dict[str, str]]:
    """
    Parses CSV text into a normalized list of record dictionaries.
    """
    records = []
    # Strip any leading BOM
    csv_text = csv_text.lstrip("\ufeff")
    reader = csv.reader(io.StringIO(csv_text))

    headers = None
    header_map = {}

    for row in reader:
        if not row or not any(cell.strip() for cell in row):
            continue

        if headers is None:
            # First non-empty row is header
            headers = [h.strip().lower() for h in row]
            for idx, h in enumerate(headers):
                clean_h = re.sub(r"[^a-z0-9]", "", h)
                if "brand" in clean_h or "make" in clean_h:
                    header_map["brand"] = idx
                elif "dealer" in clean_h:
                    header_map["dealership"] = idx
                elif "city" in clean_h:
                    header_map["city"] = idx
                elif "model" in clean_h or "car" in clean_h:
                    header_map["model"] = idx
                elif "variant" in clean_h or "trim" in clean_h:
                    header_map["variant"] = idx
                elif "fuel" in clean_h:
                    header_map["fuel"] = idx
                elif "trans" in clean_h:
                    header_map["transmission"] = idx
                elif "status" in clean_h or "avail" in clean_h:
                    header_map["status"] = idx
                elif "unit" in clean_h or "qty" in clean_h or "count" in clean_h:
                    header_map["units"] = idx
                elif "wait" in clean_h or "week" in clean_h:
                    header_map["waiting_weeks"] = idx
                elif "color" in clean_h or "colour" in clean_h:
                    header_map["colors"] = idx
                elif "note" in clean_h or "promo" in clean_h:
                    header_map["promo_note"] = idx
            continue

        # Map data row
        def get_val(key: str, default: str = "") -> str:
            if key in header_map and header_map[key] < len(row):
                return row[header_map[key]].strip()
            return default

        model = get_val("model")
        variant = get_val("variant")

        # Skip rows without model or variant
        if not model or not variant:
            continue

        record = {
            "brand": get_val("brand", ""),
            "dealership": get_val("dealership", "Bajrang Motors"),
            "city": get_val("city", "Haldwani"),
            "model": model,
            "variant": variant,
            "fuel": get_val("fuel", "Diesel"),
            "transmission": get_val("transmission", "Manual"),
            "status": normalize_status(get_val("status", "IN_STOCK")),
            "units": int(re.sub(r"[^\d]", "", get_val("units", "1")) or "1"),
            "waiting_weeks": int(re.sub(r"[^\d]", "", get_val("waiting_weeks", "0")) or "0"),
            "colors": get_val("colors", "Everest White, Stealth Black"),
            "promo_note": get_val("promo_note", "")
        }
        records.append(record)

    return records

def sync_inventory_from_records(records: List[Dict[str, str]]) -> Dict[str, any]:
    """
    Synchronizes parsed CSV records into the SQLite database.
    """
    if not records:
        raise ValueError("No valid vehicle stock rows found in the provided spreadsheet.")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Load existing dealerships map
    cursor.execute("SELECT id, name, city, brand FROM dealerships;")
    dealer_rows = cursor.fetchall()
    dealers = [dict(d) for d in dealer_rows]

    def find_dealer_id(d_name: str, d_city: str, d_brand: str = "") -> int:
        norm_name = d_name.lower().strip()
        norm_city = d_city.lower().strip()
        norm_brand = d_brand.lower().strip()

        # Match by name and city
        for d in dealers:
            if norm_city in d["city"].lower() and (norm_name in d["name"].lower() or d["name"].lower() in norm_name):
                return d["id"]

        # Match by name alone
        for d in dealers:
            if norm_name in d["name"].lower() or d["name"].lower() in norm_name:
                return d["id"]

        # Match by brand and city
        if norm_brand:
            for d in dealers:
                if norm_city in d["city"].lower() and norm_brand in d["brand"].lower():
                    return d["id"]

        # Match by city alone
        for d in dealers:
            if norm_city in d["city"].lower():
                return d["id"]

        # Default to first dealer (Haldwani)
        return dealers[0]["id"] if dealers else 1

    # Load existing cars map
    cursor.execute("SELECT id, make, model, slug FROM cars;")
    cars_rows = cursor.fetchall()
    cars_map = {c["model"].lower(): c["id"] for c in cars_rows}
    for c in cars_rows:
        cars_map[f"{c['make']} {c['model']}".lower()] = c["id"]
        short_make = c["make"].replace(" Motors", "")
        cars_map[f"{short_make} {c['model']}".lower()] = c["id"]
    cars_slug_map = {c["slug"]: c["id"] for c in cars_rows}

    # Load existing variants map: (car_id, variant_name.lower()) -> variant_id
    cursor.execute("SELECT id, car_id, name FROM variants;")
    variant_rows = cursor.fetchall()
    variants_map = {(v["car_id"], v["name"].lower()): v["id"] for v in variant_rows}

    # Clear current inventory and re-populate from sheet records
    cursor.execute("DELETE FROM inventory;")

    inserted_count = 0

    for rec in records:
        raw_brand = rec.get("brand", "").strip()
        dealer_id = find_dealer_id(rec["dealership"], rec["city"], raw_brand)

        # Determine brand/make
        model_name = rec["model"].strip()
        make = raw_brand if raw_brand else "Mahindra"
        known_prefixes = [
            ("tata motors", "Tata Motors"), ("tata", "Tata Motors"),
            ("mahindra", "Mahindra"),
            ("hyundai", "Hyundai"),
            ("kia", "Kia"),
            ("toyota", "Toyota"),
            ("maruti suzuki", "Maruti Suzuki"), ("maruti", "Maruti Suzuki"),
            ("nissan", "Nissan"),
            ("skoda", "Skoda"),
            ("volkswagen", "Volkswagen"), ("vw", "Volkswagen")
        ]
        for pfx, official_brand in known_prefixes:
            if model_name.lower().startswith(pfx):
                make = official_brand
                break

        car_id = cars_map.get(model_name.lower())
        if not car_id and not any(model_name.lower().startswith(pfx[0]) for pfx in known_prefixes):
            car_id = cars_map.get(f"{make} {model_name}".lower())

        if not car_id:
            car_id = cars_map.get(model_name.lower())
        if not car_id:
            # Create car
            slug = re.sub(r"[^a-z0-9]+", "-", model_name.lower()).strip("-")
            cursor.execute("""
                INSERT INTO cars (make, model, slug, category, price_range, min_price, max_price, hero_image, fuel_types, transmissions, popular_choice)
                VALUES (?, ?, ?, 'SUV', 'Available on inquiry', 0, 0, '', ?, ?, 1);
            """, (make, model_name, slug, rec["fuel"], rec["transmission"]))
            car_id = cursor.lastrowid
            cars_map[model_name.lower()] = car_id

        # Find or create variant
        var_name = rec["variant"].strip()
        var_key = (car_id, var_name.lower())
        variant_id = variants_map.get(var_key)

        if not variant_id:
            cursor.execute("""
                INSERT INTO variants (car_id, name, fuel_type, transmission, drivetrain, seating, ex_showroom_price)
                VALUES (?, ?, ?, ?, '2WD', '5-Seater', 0);
            """, (car_id, var_name, rec["fuel"], rec["transmission"]))
            variant_id = cursor.lastrowid
            variants_map[var_key] = variant_id

        # Insert inventory row
        cursor.execute("""
            INSERT INTO inventory (dealership_id, variant_id, status, units_available, waiting_period_weeks, colors_available, test_drive_available, promo_note, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, 1, ?, CURRENT_TIMESTAMP);
        """, (dealer_id, variant_id, rec["status"], rec["units"], rec["waiting_weeks"], rec["colors"], rec["promo_note"]))
        inserted_count += 1

    conn.commit()
    conn.close()

    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    set_setting("last_sync_time", now_iso)
    set_setting("last_sync_status", f"Success: {inserted_count} vehicles updated")
    set_setting("last_sync_count", str(inserted_count))

    return {
        "success": True,
        "updated_count": inserted_count,
        "timestamp": now_iso
    }

def sync_from_google_sheet_url(url: str) -> Dict[str, any]:
    """
    Full pipeline: fetches Google Sheet CSV, parses rows, and updates the database.
    """
    csv_text = fetch_sheets_csv(url)
    records = parse_csv_records(csv_text)
    result = sync_inventory_from_records(records)
    set_setting("google_sheet_url", url.strip())
    return result

def generate_sample_csv() -> str:
    """
    Generates a pre-filled sample CSV string based on the existing database stock
    so the user can import it directly into Google Sheets.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            c.make as brand,
            d.name as dealership,
            d.city,
            c.model,
            v.name as variant,
            v.fuel_type as fuel,
            v.transmission,
            i.status,
            i.units_available as units,
            i.waiting_period_weeks as waiting_weeks,
            i.colors_available as colors,
            i.promo_note
        FROM inventory i
        JOIN dealerships d ON i.dealership_id = d.id
        JOIN variants v ON i.variant_id = v.id
        JOIN cars c ON v.car_id = c.id
        ORDER BY c.make, d.city, c.model;
    """)
    rows = cursor.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(CSV_HEADERS)

    for r in rows:
        writer.writerow([
            r["brand"],
            r["dealership"],
            r["city"],
            r["model"],
            r["variant"],
            r["fuel"],
            r["transmission"],
            r["status"],
            r["units"],
            r["waiting_weeks"],
            r["colors"] or "",
            r["promo_note"] or ""
        ])

    return output.getvalue()
