import sqlite3
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "scoutmycar.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Dealerships table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dealerships (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        brand TEXT NOT NULL DEFAULT 'Mahindra',
        name TEXT NOT NULL,
        slug TEXT UNIQUE NOT NULL,
        city TEXT NOT NULL,
        rto_code TEXT NOT NULL,
        address TEXT NOT NULL,
        phone TEXT NOT NULL,
        whatsapp TEXT NOT NULL,
        manager_name TEXT,
        rating REAL DEFAULT 4.8,
        reviews_count INTEGER DEFAULT 120,
        timings TEXT DEFAULT '9:30 AM - 7:30 PM (Mon-Sun)',
        map_embed_query TEXT
    );
    """)

    # Cars table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cars (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        make TEXT NOT NULL DEFAULT 'Mahindra',
        model TEXT NOT NULL,
        slug TEXT UNIQUE NOT NULL,
        tagline TEXT,
        category TEXT NOT NULL,
        price_range TEXT NOT NULL,
        min_price INTEGER NOT NULL,
        max_price INTEGER NOT NULL,
        hero_image TEXT NOT NULL,
        brochure_url TEXT,
        fuel_types TEXT NOT NULL,
        transmissions TEXT NOT NULL,
        popular_choice INTEGER DEFAULT 0
    );
    """)

    # Variants table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS variants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        car_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        fuel_type TEXT NOT NULL,
        transmission TEXT NOT NULL,
        drivetrain TEXT NOT NULL DEFAULT '2WD',
        seating TEXT NOT NULL DEFAULT '5-Seater',
        engine_spec TEXT,
        ex_showroom_price INTEGER NOT NULL,
        key_features TEXT,
        FOREIGN KEY (car_id) REFERENCES cars(id)
    );
    """)

    # Inventory table (Dealership x Variant stock)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dealership_id INTEGER NOT NULL,
        variant_id INTEGER NOT NULL,
        status TEXT NOT NULL, -- 'IN_STOCK', 'IN_TRANSIT', 'WAITLIST'
        units_available INTEGER DEFAULT 0,
        waiting_period_weeks INTEGER DEFAULT 0,
        colors_available TEXT,
        test_drive_available INTEGER DEFAULT 1,
        promo_note TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (dealership_id) REFERENCES dealerships(id),
        FOREIGN KEY (variant_id) REFERENCES variants(id)
    );
    """)

    # Inquiries table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inquiries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dealership_id INTEGER NOT NULL,
        car_id INTEGER,
        variant_id INTEGER,
        customer_name TEXT NOT NULL,
        customer_phone TEXT NOT NULL,
        customer_email TEXT,
        customer_city TEXT NOT NULL,
        inquiry_type TEXT NOT NULL, -- 'availability_check', 'test_drive', 'price_quote', 'instant_booking'
        preferred_date TEXT,
        preferred_time TEXT,
        buying_timeline TEXT, -- '0-15 days', '15 - 30 days', '30 - 60 days', 'just enquiring'
        finance_required TEXT DEFAULT 'not decided yet', -- 'yes', 'no', 'not decided yet'
        exchange_required INTEGER DEFAULT 0,
        exchange_car_details TEXT,
        notes TEXT,
        status TEXT DEFAULT 'NEW', -- 'NEW', 'CONTACTED', 'TEST_DRIVE_DONE', 'CLOSED'
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (dealership_id) REFERENCES dealerships(id),
        FOREIGN KEY (car_id) REFERENCES cars(id),
        FOREIGN KEY (variant_id) REFERENCES variants(id)
    );
    """)

    # Stock Alerts table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock_alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT NOT NULL,
        customer_phone TEXT NOT NULL,
        car_id INTEGER NOT NULL,
        preferred_city TEXT NOT NULL,
        preferred_color TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (car_id) REFERENCES cars(id)
    );
    """)

    # Admin Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admin_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        name TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'super_admin', -- 'super_admin', 'dealer_manager'
        dealership_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (dealership_id) REFERENCES dealerships(id)
    );
    """)

    # Active Sessions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        session_token TEXT PRIMARY KEY,
        user_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP NOT NULL,
        FOREIGN KEY (user_id) REFERENCES admin_users(id)
    );
    """)

    # App Settings table (key-value store for Google Sheets URL, sync status, etc.)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS app_settings (
        key TEXT PRIMARY KEY,
        value TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Migrations for existing databases
    cursor.execute("PRAGMA table_info(dealerships);")
    d_cols = [c[1] for c in cursor.fetchall()]
    if "brand" not in d_cols:
        cursor.execute("ALTER TABLE dealerships ADD COLUMN brand TEXT NOT NULL DEFAULT 'Mahindra';")

    cursor.execute("PRAGMA table_info(inquiries);")
    inq_cols = [c[1] for c in cursor.fetchall()]
    if "finance_required" not in inq_cols:
        cursor.execute("ALTER TABLE inquiries ADD COLUMN finance_required TEXT DEFAULT 'not decided yet';")
    if "customer_email" not in inq_cols:
        cursor.execute("ALTER TABLE inquiries ADD COLUMN customer_email TEXT;")

    conn.commit()
    conn.close()

def get_setting(key: str, default: str = None) -> str:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM app_settings WHERE key = ?;", (key,))
    row = cursor.fetchone()
    conn.close()
    return row["value"] if row else default

def set_setting(key: str, value: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO app_settings (key, value, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = CURRENT_TIMESTAMP;
    """, (key, value))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")
