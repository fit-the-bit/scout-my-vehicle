import csv
import os
import re
from pathlib import Path
from collections import defaultdict

from app.database import get_db_connection, init_db
from app.auth import hash_password

BASE_DIR = Path(__file__).resolve().parent
VARIANTS_CSV = BASE_DIR / "data" / "variants.csv"

# Brand mapping for all 87 models in CSV
BRAND_MAPPING = {
    # Maruti Suzuki (18)
    "Alto K10": "Maruti Suzuki",
    "S-Presso": "Maruti Suzuki",
    "Celerio": "Maruti Suzuki",
    "Wagon R": "Maruti Suzuki",
    "Swift": "Maruti Suzuki",
    "Dzire": "Maruti Suzuki",
    "Brezza": "Maruti Suzuki",
    "Ertiga": "Maruti Suzuki",
    "Eeco": "Maruti Suzuki",
    "Victoris": "Maruti Suzuki",
    "Ignis": "Maruti Suzuki",
    "Baleno": "Maruti Suzuki",
    "Fronx": "Maruti Suzuki",
    "Ciaz": "Maruti Suzuki",
    "Jimny": "Maruti Suzuki",
    "Grand Vitara": "Maruti Suzuki",
    "XL6": "Maruti Suzuki",
    "Invicto": "Maruti Suzuki",

    # Nissan (2)
    "Magnite": "Nissan",
    "X-Trail": "Nissan",

    # Skoda (4)
    "Slavia": "Skoda",
    "Kylaq": "Skoda",
    "Kushaq": "Skoda",
    "Kodiaq": "Skoda",

    # Tata Motors (14)
    "Tiago": "Tata Motors",
    "Tiago EV": "Tata Motors",
    "Tigor": "Tata Motors",
    "Altroz": "Tata Motors",
    "Punch": "Tata Motors",
    "Punch EV": "Tata Motors",
    "Nexon": "Tata Motors",
    "Nexon EV": "Tata Motors",
    "Curvv": "Tata Motors",
    "Curvv EV": "Tata Motors",
    "Harrier": "Tata Motors",
    "Safari": "Tata Motors",
    "Sierra": "Tata Motors",
    "Sierra EV": "Tata Motors",

    # Toyota (11)
    "Glanza": "Toyota",
    "Urban Cruiser Taisor": "Toyota",
    "Urban Cruiser Hyryder": "Toyota",
    "Innova Crysta": "Toyota",
    "Innova Hycross": "Toyota",
    "Fortuner": "Toyota",
    "Fortuner Legender": "Toyota",
    "Hilux": "Toyota",
    "Camry": "Toyota",
    "Vellfire": "Toyota",
    "Land Cruiser 300": "Toyota",

    # Volkswagen (3)
    "Virtus": "Volkswagen",
    "Taigun": "Volkswagen",
    "Tiguan": "Volkswagen",

    # Hyundai (14)
    "Grand i10 Nios": "Hyundai",
    "i20": "Hyundai",
    "i20 N Line": "Hyundai",
    "Aura": "Hyundai",
    "Exter": "Hyundai",
    "Venue": "Hyundai",
    "Venue N Line": "Hyundai",
    "Verna": "Hyundai",
    "Creta": "Hyundai",
    "Creta N Line": "Hyundai",
    "Alcazar": "Hyundai",
    "Tucson": "Hyundai",
    "Ioniq 5": "Hyundai",
    "Creta EV": "Hyundai",

    # Kia (9)
    "Sonet": "Kia",
    "Seltos": "Kia",
    "Carens": "Kia",
    "EV6": "Kia",
    "EV9": "Kia",
    "Carnival": "Kia",
    "Syros (Clavis)": "Kia",
    "Syros EV (Clavis EV)": "Kia",
    "Sorento": "Kia",

    # Mahindra (12)
    "Scorpio N": "Mahindra",
    "Scorpio Classic": "Mahindra",
    "Thar": "Mahindra",
    "Thar Roxx": "Mahindra",
    "XUV 3XO": "Mahindra",
    "XUV700": "Mahindra",
    "XUV400 EV": "Mahindra",
    "Bolero": "Mahindra",
    "Bolero Neo": "Mahindra",
    "XUV 3XO EV": "Mahindra",
    "XEV 9e": "Mahindra",
    "XEV 9s": "Mahindra",
}

CATEGORY_MAP = {
    "Alto K10": "Entry Hatchback", "S-Presso": "Mini Hatchback", "Celerio": "Hatchback",
    "Wagon R": "Tallboy Hatchback", "Swift": "Hatchback", "Dzire": "Compact Sedan",
    "Brezza": "Compact SUV", "Ertiga": "7-Seater MPV", "Eeco": "Utility Van",
    "Victoris": "Compact SUV", "Ignis": "Urban Compact", "Baleno": "Premium Hatchback",
    "Fronx": "Compact Crossover", "Ciaz": "Mid-size Sedan", "Jimny": "Lifestyle 4x4",
    "Grand Vitara": "Mid-size SUV", "XL6": "Premium 6-Seater MPV", "Invicto": "Premium Hybrid MPV",
    "Magnite": "Compact SUV", "X-Trail": "Premium SUV",
    "Slavia": "Mid-size Sedan", "Kylaq": "Compact SUV", "Kushaq": "Mid-size SUV", "Kodiaq": "Luxury 7-Seater SUV",
    "Tiago": "Hatchback", "Tiago EV": "Electric Hatchback", "Tigor": "Compact Sedan",
    "Altroz": "Premium Hatchback", "Punch": "Micro SUV", "Punch EV": "Electric Micro SUV",
    "Nexon": "Subcompact SUV", "Nexon EV": "Electric SUV", "Curvv": "Coupe SUV",
    "Curvv EV": "Electric Coupe SUV", "Harrier": "Mid-size SUV", "Safari": "Flagship 7-Seater SUV",
    "Sierra": "Lifestyle SUV", "Sierra EV": "Electric Lifestyle SUV",
    "Glanza": "Premium Hatchback", "Urban Cruiser Taisor": "Compact Crossover",
    "Urban Cruiser Hyryder": "Mid-size Hybrid SUV", "Innova Crysta": "Premium MPV",
    "Innova Hycross": "Luxury Hybrid MPV", "Fortuner": "Full-size SUV",
    "Fortuner Legender": "Flagship 4x4 SUV", "Hilux": "Lifestyle Pickup Truck",
    "Camry": "Luxury Hybrid Sedan", "Vellfire": "Ultra-Luxury Lounge MPV",
    "Land Cruiser 300": "Iconic Luxury 4x4",
    "Virtus": "Premium Sedan", "Taigun": "Mid-size SUV", "Tiguan": "Flagship German SUV",
    "Grand i10 Nios": "Hatchback", "i20": "Premium Hatchback", "i20 N Line": "Performance Hatchback",
    "Aura": "Compact Sedan", "Exter": "Micro SUV", "Venue": "Compact SUV",
    "Venue N Line": "Performance SUV", "Verna": "Futuristic Sedan", "Creta": "Mid-size SUV",
    "Creta N Line": "Performance SUV", "Alcazar": "Premium 7-Seater SUV", "Tucson": "Premium Luxury SUV",
    "Ioniq 5": "Flagship Electric EV", "Creta EV": "Electric Mid-size SUV",
    "Sonet": "Compact SUV", "Seltos": "Mid-size SUV", "Carens": "3-Row Recreational MPV",
    "EV6": "Electric Crossover", "EV9": "Luxury 3-Row Electric SUV", "Carnival": "Limousine MPV",
    "Syros (Clavis)": "Compact SUV", "Syros EV (Clavis EV)": "Electric Compact SUV", "Sorento": "Premium Mid-size SUV",
    "Scorpio N": "D-Segment SUV", "Scorpio Classic": "Legendary SUV", "Thar": "Pure Off-roader 4x4",
    "Thar Roxx": "5-Door Off-road Icon", "XUV 3XO": "Compact SUV", "XUV700": "Intelligent Luxury SUV",
    "XUV400 EV": "Electric SUV", "Bolero": "Undisputed Workhorse", "Bolero Neo": "Tough Utility SUV",
    "XUV 3XO EV": "Electric Compact SUV", "XEV 9e": "Electric Luxury Coupe SUV", "XEV 9s": "Electric Luxury SUV"
}

BASE_PRICES = {
    # Maruti Suzuki
    "Alto K10": 399000, "S-Presso": 426000, "Celerio": 536000, "Wagon R": 554000,
    "Eeco": 532000, "Ignis": 584000, "Swift": 649000, "Dzire": 679000,
    "Baleno": 666000, "Fronx": 751000, "Brezza": 834000, "Ertiga": 869000,
    "Ciaz": 940000, "XL6": 1161000, "Jimny": 1274000, "Grand Vitara": 1087000,
    "Victoris": 1087000, "Invicto": 2521000,

    # Nissan
    "Magnite": 599000, "X-Trail": 4992000,

    # Skoda
    "Kylaq": 789000, "Slavia": 1069000, "Kushaq": 1089000, "Kodiaq": 3999000,

    # Tata Motors
    "Tiago": 565000, "Tiago EV": 799000, "Tigor": 630000, "Altroz": 665000,
    "Punch": 613000, "Punch EV": 999000, "Nexon": 800000, "Nexon EV": 1249000,
    "Curvv": 999000, "Curvv EV": 1749000, "Harrier": 1549000, "Safari": 1619000,
    "Sierra": 1499000, "Sierra EV": 1899000,

    # Toyota
    "Glanza": 686000, "Urban Cruiser Taisor": 773000, "Urban Cruiser Hyryder": 1114000,
    "Innova Crysta": 1999000, "Innova Hycross": 1977000, "Hilux": 3040000,
    "Fortuner": 3343000, "Fortuner Legender": 4366000, "Camry": 4617000,
    "Vellfire": 12230000, "Land Cruiser 300": 21000000,

    # Volkswagen
    "Virtus": 1156000, "Taigun": 1170000, "Tiguan": 3517000,

    # Hyundai
    "Grand i10 Nios": 592000, "Aura": 649000, "Exter": 613000, "i20": 704000,
    "i20 N Line": 999000, "Venue": 794000, "Venue N Line": 1207000, "Verna": 1100000,
    "Creta": 1100000, "Creta N Line": 1682000, "Creta EV": 1799000, "Alcazar": 1499000,
    "Tucson": 2902000, "Ioniq 5": 4605000,

    # Kia
    "Sonet": 799000, "Syros (Clavis)": 899000, "Syros EV (Clavis EV)": 1399000,
    "Seltos": 1090000, "Carens": 1052000, "Carnival": 6390000, "EV6": 6097000,
    "EV9": 12990000, "Sorento": 3800000,

    # Mahindra
    "Bolero": 979000, "Bolero Neo": 995000, "XUV 3XO": 779000, "XUV 3XO EV": 1399000,
    "Thar": 1135000, "Thar Roxx": 1299000, "Scorpio Classic": 1362000, "Scorpio N": 1385000,
    "XUV700": 1399000, "XUV400 EV": 1549000, "XEV 9e": 2190000, "XEV 9s": 2290000
}

BRAND_COLORS = {
    "Maruti Suzuki": [
        "Pearl Arctic White", "Magma Grey", "Splendid Silver", "Nexa Blue",
        "Sizzling Red", "Grandeur Grey", "Brave Khaki", "Bluish Black", "Luster Blue"
    ],
    "Nissan": [
        "Blade Silver", "Onyx Black", "Flare Garnet Red", "Pearl White",
        "Vivid Blue", "Tourmaline Brown"
    ],
    "Skoda": [
        "Candy White", "Carbon Steel", "Brilliant Silver", "Tornado Red",
        "Lava Blue", "Deep Black"
    ],
    "Tata Motors": [
        "Pristine White", "Daytona Grey", "Calgary White", "Flame Red",
        "Pure Grey", "Cosmic Gold", "Sunlit Yellow", "Fearless Purple", "Oberon Black"
    ],
    "Toyota": [
        "Super White", "Platinum White Pearl", "Attitude Black", "Cafe White",
        "Gaming Grey", "Sporting Red", "Enticing Silver", "Blackish Ageha Glass Flake"
    ],
    "Volkswagen": [
        "Candy White", "Carbon Steel Grey", "Reflex Silver", "Wild Cherry Red",
        "Rising Blue", "Curcuma Yellow", "Deep Black Pearl"
    ],
    "Hyundai": [
        "Atlas White", "Abyss Black", "Titan Grey", "Ranger Khaki",
        "Robust Emerald Pearl", "Starry Night", "Fiery Red", "Cosmic Blue"
    ],
    "Kia": [
        "Glacier White Pearl", "Aurora Black Pearl", "Gravity Grey", "Pewter Olive",
        "Intense Red", "Imperial Blue", "Sparkling Silver", "Clear White"
    ],
    "Mahindra": [
        "Everest White", "Stealth Black", "Napoli Black", "Deep Forest",
        "Dazzling Silver", "Tango Red", "Battleship Grey", "Red Rage", "Electric Blue"
    ]
}

POPULAR_MODELS = {
    "Swift", "Dzire", "Brezza", "Baleno", "Fronx", "Grand Vitara", "Ertiga",
    "Nexon", "Punch", "Curvv", "Harrier", "Safari",
    "Creta", "Venue", "Exter", "Verna",
    "Seltos", "Sonet", "Carens",
    "Fortuner", "Innova Hycross", "Urban Cruiser Hyryder", "Glanza",
    "Thar Roxx", "Scorpio N", "XUV700", "XUV 3XO", "Thar", "Bolero",
    "Slavia", "Kushaq", "Virtus", "Taigun", "Magnite"
}

def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")

def get_car_slug(make: str, model: str) -> str:
    m_slug = slugify(model)
    if make == "Tata Motors":
        return f"tata-{m_slug}"
    elif make == "Maruti Suzuki":
        return f"maruti-suzuki-{m_slug}"
    elif make == "Mahindra":
        return f"mahindra-{m_slug}"
    elif make == "Hyundai":
        return f"hyundai-{m_slug}"
    elif make == "Kia":
        return f"kia-{m_slug}"
    elif make == "Toyota":
        return f"toyota-{m_slug}"
    elif make == "Nissan":
        return f"nissan-{m_slug}"
    elif make == "Skoda":
        return f"skoda-{m_slug}"
    elif make == "Volkswagen":
        return f"volkswagen-{m_slug}"
    return f"{slugify(make)}-{m_slug}"

def format_price_range(min_p: int, max_p: int) -> str:
    if min_p >= 10000000 or max_p >= 10000000:
        min_str = f"₹ {min_p / 10000000:.2f} Cr" if min_p >= 10000000 else f"₹ {min_p / 100000:.2f} Lakh"
        max_str = f"₹ {max_p / 10000000:.2f} Cr"
        return f"{min_str} - {max_str}" if min_p != max_p else min_str
    return f"₹ {min_p / 100000:.2f} - {max_p / 100000:.2f} Lakh"

def normalize_transmission_display(t_code: str) -> str:
    t_code = t_code.strip()
    if t_code == "MT":
        return "Manual (MT)"
    elif t_code == "AT":
        return "Automatic (AT)"
    return t_code

def seed():
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    # Clear existing data
    cursor.execute("DELETE FROM inventory;")
    cursor.execute("DELETE FROM variants;")
    cursor.execute("DELETE FROM cars;")
    cursor.execute("DELETE FROM dealerships;")
    cursor.execute("DELETE FROM inquiries;")
    cursor.execute("DELETE FROM stock_alerts;")
    try:
        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('dealerships', 'cars', 'variants', 'inventory', 'inquiries', 'stock_alerts');")
    except Exception:
        pass

    # 1. Insert 18 Dealerships across 9 Brands in Haldwani & Rudrapur
    dealerships_data = [
        # Tata Motors
        (
            "Tata Motors", "Gola Ganapati Motors", "gola-ganapati-tata-haldwani", "Haldwani", "UK-04",
            "Rampur Road, Near Transport Nagar, Haldwani, Uttarakhand 263139",
            "+91 5946 221 400", "919837012341", "Sanjay Joshi (Sales Head)",
            4.8, 290, "9:30 AM - 7:30 PM", "Gola Ganapati Motors Tata Haldwani"
        ),
        (
            "Tata Motors", "Amit Auto", "amit-auto-tata-rudrapur", "Rudrapur", "UK-06",
            "Kashipur Road, Near Danpur, Rudrapur, Uttarakhand 263153",
            "+91 5944 242 110", "919837167891", "Pankaj Bisht (General Manager)",
            4.7, 210, "9:30 AM - 7:00 PM", "Amit Auto Tata Rudrapur"
        ),

        # Mahindra
        (
            "Mahindra", "Bajrang Motors", "bajrang-motors-mahindra-haldwani", "Haldwani", "UK-04",
            "Bareilly - Nainital National Highway, Kathgodam Road, Haldwani, Uttarakhand 263139",
            "+91 5946 220 188", "919837012345", "Rajesh Rawat (Sales Head)",
            4.9, 350, "9:00 AM - 7:30 PM", "Bajrang Motors Mahindra Haldwani"
        ),
        (
            "Mahindra", "Kumar Autowheels", "kumar-autowheels-mahindra-rudrapur", "Rudrapur", "UK-06",
            "Delhi - Nainital Highway (NH-109), Near Metropolis Mall, Rudrapur, Uttarakhand 263153",
            "+91 5944 245 880", "919837167890", "Harish Joshi (Branch Manager)",
            4.8, 280, "9:00 AM - 7:30 PM", "Kumar Autowheels Mahindra Rudrapur"
        ),

        # Hyundai
        (
            "Hyundai", "Sachin Hyundai", "sachin-hyundai-haldwani", "Haldwani", "UK-04",
            "Nainital Road, Near Tikonia, Haldwani, Uttarakhand 263139",
            "+91 5946 250 333", "919837012342", "Sunil Pandey (Manager)",
            4.8, 310, "9:30 AM - 7:30 PM", "Sachin Hyundai Haldwani"
        ),
        (
            "Hyundai", "Bindal Hyundai", "bindal-hyundai-rudrapur", "Rudrapur", "UK-06",
            "Kichha Road, Opposite District Hospital, Rudrapur, Uttarakhand 263153",
            "+91 5944 252 800", "919837167892", "Vipin Chandra (GM)",
            4.7, 240, "9:30 AM - 7:00 PM", "Bindal Hyundai Rudrapur"
        ),

        # Kia
        (
            "Kia", "Classic Kia", "classic-kia-haldwani", "Haldwani", "UK-04",
            "Kaladhungi Road, Near Kusumkhera, Haldwani, Uttarakhand 263139",
            "+91 5946 261 500", "919837012343", "Mohit Tiwari (Sales Lead)",
            4.9, 275, "9:30 AM - 7:30 PM", "Classic Kia Haldwani"
        ),
        (
            "Kia", "Classic Kia", "classic-kia-rudrapur", "Rudrapur", "UK-06",
            "Kashipur Bypass, Near Big Bazaar Chowk, Rudrapur, Uttarakhand 263153",
            "+91 5944 260 112", "919837167893", "Deepak Bhatt (Showroom Incharge)",
            4.8, 220, "9:30 AM - 7:00 PM", "Classic Kia Rudrapur"
        ),

        # Toyota
        (
            "Toyota", "Trust Toyota", "trust-toyota-haldwani", "Haldwani", "UK-04",
            "Rampur Road, Near ITI, Haldwani, Uttarakhand 263139",
            "+91 5946 280 900", "919837012344", "Girish Pathak (Sales Manager)",
            4.9, 390, "9:00 AM - 7:30 PM", "Trust Toyota Haldwani"
        ),
        (
            "Toyota", "Trust Toyota", "trust-toyota-rudrapur", "Rudrapur", "UK-06",
            "NH-109, Opp. Radisson Blu Hotel, Rudrapur, Uttarakhand 263153",
            "+91 5944 270 450", "919837167894", "Arun Chauhan (Branch Head)",
            4.8, 260, "9:00 AM - 7:00 PM", "Trust Toyota Rudrapur"
        ),

        # Maruti Suzuki
        (
            "Maruti Suzuki", "Nanital Moters", "nanital-moters-maruti-haldwani", "Haldwani", "UK-04",
            "Bareilly Road, Motahaldu, Haldwani, Uttarakhand 263139",
            "+91 5946 235 600", "919837012346", "Ramesh Danu (Sales Head)",
            4.8, 420, "9:00 AM - 8:00 PM", "Nanital Moters Maruti Haldwani"
        ),
        (
            "Maruti Suzuki", "Akansha Automobiles", "akansha-automobiles-maruti-rudrapur", "Rudrapur", "UK-06",
            "Kashipur Road, Near Transit Camp, Rudrapur, Uttarakhand 263153",
            "+91 5944 246 700", "919837167895", "Kailash Upadhyay (General Manager)",
            4.7, 380, "9:00 AM - 8:00 PM", "Akansha Automobiles Maruti Rudrapur"
        ),

        # Nissan
        (
            "Nissan", "Hind Nissan", "hind-nissan-haldwani", "Haldwani", "UK-04",
            "Rampur Road, Near Transport Nagar, Haldwani, Uttarakhand 263139",
            "+91 5946 228 100", "919837012347", "Amit Verma (Sales Head)",
            4.7, 195, "9:30 AM - 7:30 PM", "Hind Nissan Haldwani"
        ),
        (
            "Nissan", "Hind Nissan", "hind-nissan-rudrapur", "Rudrapur", "UK-06",
            "Kashipur Road, Near Danpur, Rudrapur, Uttarakhand 263153",
            "+91 5944 249 200", "919837167896", "Rohit Chauhan (General Manager)",
            4.6, 160, "9:30 AM - 7:00 PM", "Hind Nissan Rudrapur"
        ),

        # Skoda
        (
            "Skoda", "Frontline Skoda", "frontline-skoda-haldwani", "Haldwani", "UK-04",
            "Bareilly Road, Motahaldu, Haldwani, Uttarakhand 263139",
            "+91 5946 239 500", "919837012348", "Neeraj Joshi (Showroom Manager)",
            4.8, 215, "9:30 AM - 7:30 PM", "Frontline Skoda Haldwani"
        ),
        (
            "Skoda", "Frontline Skoda", "frontline-skoda-rudrapur", "Rudrapur", "UK-06",
            "Delhi-Nainital Highway (NH-109), Near Metropolis Mall, Rudrapur, Uttarakhand 263153",
            "+91 5944 248 300", "919837167897", "Alok Pandey (Branch Head)",
            4.7, 180, "9:30 AM - 7:00 PM", "Frontline Skoda Rudrapur"
        ),

        # Volkswagen
        (
            "Volkswagen", "Frontline Volkswagen", "frontline-volkswagen-haldwani", "Haldwani", "UK-04",
            "Bareilly Road, Goraparav, Haldwani, Uttarakhand 263139",
            "+91 5946 242 800", "919837012349", "Deepak Mehta (Sales Manager)",
            4.8, 230, "9:30 AM - 7:30 PM", "Frontline Volkswagen Haldwani"
        ),
        (
            "Volkswagen", "Frontline Volkswagen", "frontline-volkswagen-rudrapur", "Rudrapur", "UK-06",
            "NH-109, Opp. Radisson Blu Hotel, Rudrapur, Uttarakhand 263153",
            "+91 5944 256 900", "919837167898", "Sandeep Rawat (Branch Manager)",
            4.7, 190, "9:30 AM - 7:00 PM", "Frontline Volkswagen Rudrapur"
        ),
    ]

    for d in dealerships_data:
        cursor.execute("""
        INSERT INTO dealerships (brand, name, slug, city, rto_code, address, phone, whatsapp, manager_name, rating, reviews_count, timings, map_embed_query)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, d)

    cursor.execute("SELECT id, slug, brand, city FROM dealerships;")
    dealer_rows = cursor.fetchall()
    dealer_ids = {r["slug"]: r["id"] for r in dealer_rows}
    brand_dealers = defaultdict(list)
    for r in dealer_rows:
        brand_dealers[r["brand"]].append((r["city"], r["id"]))

    # 2. Read Variants CSV and group by Model
    if not VARIANTS_CSV.exists():
        raise FileNotFoundError(f"Variants CSV not found at {VARIANTS_CSV}")

    csv_rows = []
    with open(VARIANTS_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            csv_rows.append(row)

    model_variants = defaultdict(list)
    models_order = []
    for r in csv_rows:
        m = r["Model"].strip()
        if m not in model_variants:
            models_order.append(m)
        model_variants[m].append(r)

    # 3. Insert Cars & Variants
    car_id_map = {}
    variant_records = []

    for model_name in models_order:
        make = BRAND_MAPPING.get(model_name, "Maruti Suzuki")
        slug = get_car_slug(make, model_name)
        category = CATEGORY_MAP.get(model_name, "SUV")
        base_p = BASE_PRICES.get(model_name, 800000)
        v_list = model_variants[model_name]

        fuels_set = []
        for v in v_list:
            f_val = v["Fuel"].strip()
            if f_val not in fuels_set:
                fuels_set.append(f_val)
        fuels_str = ", ".join(fuels_set)

        trans_set = []
        for v in v_list:
            t_val = v["Transmission"].strip()
            if t_val not in trans_set:
                trans_set.append(t_val)
        trans_str = ", ".join(trans_set)

        var_prices = []
        for idx, v in enumerate(v_list):
            fuel = v["Fuel"].strip()
            trans = v["Transmission"].strip()
            trim_adder = idx * 45000
            fuel_adder = 110000 if fuel == "Diesel" else (140000 if fuel == "Hybrid" else (180000 if fuel == "Electric" else (85000 if fuel == "CNG" else (40000 if fuel == "Petrol Turbo" else 0))))
            trans_adder = 65000 if trans in ["AMT", "iMT"] else (110000 if trans in ["AT", "IVT", "CVT"] else (140000 if trans in ["DCT", "DCA", "DSG", "e-CVT"] else 0))
            calc_price = base_p + trim_adder + fuel_adder + trans_adder
            var_prices.append(calc_price)

        min_price = min(var_prices)
        max_price = max(var_prices)
        price_range = format_price_range(min_price, max_price)
        popular_choice = 1 if model_name in POPULAR_MODELS else 0
        tagline = f"The Premier {make} {model_name}"

        cursor.execute("""
        INSERT INTO cars (make, model, slug, tagline, category, price_range, min_price, max_price, hero_image, fuel_types, transmissions, popular_choice)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, '', ?, ?, ?);
        """, (make, model_name, slug, tagline, category, price_range, min_price, max_price, fuels_str, trans_str, popular_choice))

        car_id = cursor.lastrowid
        car_id_map[model_name] = car_id

        for idx, v in enumerate(v_list):
            v_name = v["Variant"].strip()
            fuel = v["Fuel"].strip()
            trans = v["Transmission"].strip()
            price = var_prices[idx]

            if any(k in v_name.lower() for k in ["4x4", "4wd", "awd"]) or model_name in ["Jimny", "Hilux", "Land Cruiser 300"]:
                drivetrain = "4x4"
            elif any(k in model_name for k in ["Fortuner", "Bolero", "Scorpio"]):
                drivetrain = "RWD"
            else:
                drivetrain = "FWD"

            if any(k in model_name for k in ["Ertiga", "Carens", "Safari", "Alcazar", "Kodiaq", "Innova Crysta"]):
                seating = "7-Seater"
            elif any(k in model_name for k in ["XL6"]):
                seating = "6-Seater"
            elif any(k in model_name for k in ["Innova Hycross", "Carnival", "Vellfire"]):
                seating = "7-Seater"
            elif any(k in model_name for k in ["Thar", "Jimny"]) and "roxx" not in model_name.lower():
                seating = "4-Seater"
            else:
                seating = "5-Seater"

            if fuel == "Electric":
                engine_spec = "Permanent Magnet AC Motor (High Capacity Battery)"
                key_features = "Fast DC Charging, Regenerative Braking, Smart Connected Car Suite"
            elif fuel == "Hybrid":
                engine_spec = "Intelligent Strong Hybrid Electric Powertrain"
                key_features = "Pure EV Driving Mode, Digital Cockpit, High Fuel Economy"
            elif fuel == "CNG":
                engine_spec = "Factory Fitted Bi-Fuel CNG Engine"
                key_features = "Twin Cylinder Boot Space, High Mileage, Dual ECU Setup"
            elif fuel == "Diesel":
                engine_spec = "CRDi / Turbo Diesel Common Rail"
                key_features = "High Peak Torque, Cruise Control, Electronic Stability Program"
            elif fuel == "Petrol Turbo":
                engine_spec = "Turbocharged Direct Injection Petrol"
                key_features = "Paddle Shifters, Sport Drive Mode, Responsive Acceleration"
            else:
                engine_spec = "Dual VVT / MPi Petrol Engine"
                key_features = "Touchscreen Infotainment, Keyless Start, Full Airbag Safety"

            trans_display = normalize_transmission_display(trans)

            cursor.execute("""
            INSERT INTO variants (car_id, name, fuel_type, transmission, drivetrain, seating, engine_spec, ex_showroom_price, key_features)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (car_id, v_name, fuel, trans_display, drivetrain, seating, engine_spec, price, key_features))

            variant_id = cursor.lastrowid
            variant_records.append({
                "variant_id": variant_id,
                "car_id": car_id,
                "model": model_name,
                "make": make,
                "name": v_name,
                "fuel": fuel,
                "transmission": trans_display,
                "idx": idx
            })

    # 4. Insert Inventory for all 671 variants
    for v_info in variant_records:
        make = v_info["make"]
        dealers = brand_dealers.get(make, [])
        if not dealers:
            dealers = [(r["city"], r["id"]) for r in dealer_rows[:2]]

        d_tuple = dealers[v_info["idx"] % len(dealers)]
        dealership_id = d_tuple[1]

        colors_list = BRAND_COLORS.get(make, ["Pristine White", "Daytona Grey", "Napoli Black"])
        start_c = (v_info["idx"] * 2) % len(colors_list)
        picked_colors = [colors_list[start_c]]
        if len(colors_list) > 1:
            picked_colors.append(colors_list[(start_c + 1) % len(colors_list)])
        colors_str = ", ".join(picked_colors)

        units = 2 + (v_info["idx"] % 3)

        cursor.execute("""
        INSERT INTO inventory (dealership_id, variant_id, status, units_available, waiting_period_weeks, colors_available, test_drive_available, promo_note)
        VALUES (?, ?, 'IN_STOCK', ?, 0, ?, 1, 'Immediate delivery from authorized dealer showroom stock.');
        """, (dealership_id, v_info["variant_id"], units, colors_str))

    # 5. Seed Staff & Admin Accounts
    cursor.execute("DELETE FROM admin_users;")
    cursor.execute("DELETE FROM sessions;")

    admin_hash, admin_salt = hash_password("scoutmycar2026")
    staff_hash, staff_salt = hash_password("staff")

    admin_users = [
        ("admin", admin_hash, admin_salt, "System Administrator", "super_admin", None),
        ("tata_haldwani", staff_hash, staff_salt, "Gola Ganapati Motors Manager", "dealer_manager", dealer_ids["gola-ganapati-tata-haldwani"]),
        ("tata_rudrapur", staff_hash, staff_salt, "Amit Auto Manager", "dealer_manager", dealer_ids["amit-auto-tata-rudrapur"]),
        ("mahindra_haldwani", staff_hash, staff_salt, "Bajrang Motors Manager", "dealer_manager", dealer_ids["bajrang-motors-mahindra-haldwani"]),
        ("mahindra_rudrapur", staff_hash, staff_salt, "Kumar Autowheels Manager", "dealer_manager", dealer_ids["kumar-autowheels-mahindra-rudrapur"]),
        ("hyundai_haldwani", staff_hash, staff_salt, "Sachin Hyundai Manager", "dealer_manager", dealer_ids["sachin-hyundai-haldwani"]),
        ("hyundai_rudrapur", staff_hash, staff_salt, "Bindal Hyundai Manager", "dealer_manager", dealer_ids["bindal-hyundai-rudrapur"]),
        ("kia_haldwani", staff_hash, staff_salt, "Classic Kia Haldwani Manager", "dealer_manager", dealer_ids["classic-kia-haldwani"]),
        ("kia_rudrapur", staff_hash, staff_salt, "Classic Kia Rudrapur Manager", "dealer_manager", dealer_ids["classic-kia-rudrapur"]),
        ("toyota_haldwani", staff_hash, staff_salt, "Trust Toyota Haldwani Manager", "dealer_manager", dealer_ids["trust-toyota-haldwani"]),
        ("toyota_rudrapur", staff_hash, staff_salt, "Trust Toyota Rudrapur Manager", "dealer_manager", dealer_ids["trust-toyota-rudrapur"]),
        ("maruti_haldwani", staff_hash, staff_salt, "Nanital Moters Manager", "dealer_manager", dealer_ids["nanital-moters-maruti-haldwani"]),
        ("maruti_rudrapur", staff_hash, staff_salt, "Akansha Automobiles Manager", "dealer_manager", dealer_ids["akansha-automobiles-maruti-rudrapur"]),
        ("nissan_haldwani", staff_hash, staff_salt, "Hind Nissan Haldwani Manager", "dealer_manager", dealer_ids["hind-nissan-haldwani"]),
        ("nissan_rudrapur", staff_hash, staff_salt, "Hind Nissan Rudrapur Manager", "dealer_manager", dealer_ids["hind-nissan-rudrapur"]),
        ("skoda_haldwani", staff_hash, staff_salt, "Frontline Skoda Haldwani Manager", "dealer_manager", dealer_ids["frontline-skoda-haldwani"]),
        ("skoda_rudrapur", staff_hash, staff_salt, "Frontline Skoda Rudrapur Manager", "dealer_manager", dealer_ids["frontline-skoda-rudrapur"]),
        ("volkswagen_haldwani", staff_hash, staff_salt, "Frontline Volkswagen Haldwani Manager", "dealer_manager", dealer_ids["frontline-volkswagen-haldwani"]),
        ("volkswagen_rudrapur", staff_hash, staff_salt, "Frontline Volkswagen Rudrapur Manager", "dealer_manager", dealer_ids["frontline-volkswagen-rudrapur"]),
    ]

    for u in admin_users:
        cursor.execute("""
        INSERT INTO admin_users (username, password_hash, salt, name, role, dealership_id)
        VALUES (?, ?, ?, ?, ?, ?);
        """, u)

    conn.commit()
    conn.close()
    print(f"Database seeded successfully with 18 authorized dealerships, {len(models_order)} car models, and {len(variant_records)} active variants across 9 brands!")

if __name__ == "__main__":
    seed()
