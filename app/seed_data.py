from app.database import get_db_connection, init_db

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

    # 1. Insert 12 Dealerships across 6 Brands in Haldwani & Rudrapur
    dealerships_data = [
        # Tata Motors
        (
            "Tata Motors",
            "Gola Ganapati Motors",
            "gola-ganapati-tata-haldwani",
            "Haldwani",
            "UK-04",
            "Rampur Road, Near Transport Nagar, Haldwani, Uttarakhand 263139",
            "+91 5946 221 400",
            "919837012341",
            "Sanjay Joshi (Sales Head)",
            4.8,
            290,
            "9:30 AM - 7:30 PM",
            "Gola Ganapati Motors Tata Haldwani"
        ),
        (
            "Tata Motors",
            "Amit Auto",
            "amit-auto-tata-rudrapur",
            "Rudrapur",
            "UK-06",
            "Kashipur Road, Near Danpur, Rudrapur, Uttarakhand 263153",
            "+91 5944 242 110",
            "919837167891",
            "Pankaj Bisht (General Manager)",
            4.7,
            210,
            "9:30 AM - 7:00 PM",
            "Amit Auto Tata Rudrapur"
        ),

        # Mahindra
        (
            "Mahindra",
            "Bajrang Motors",
            "bajrang-motors-mahindra-haldwani",
            "Haldwani",
            "UK-04",
            "Bareilly - Nainital National Highway, Kathgodam Road, Haldwani, Uttarakhand 263139",
            "+91 5946 220 188",
            "919837012345",
            "Rajesh Rawat (Sales Head)",
            4.9,
            350,
            "9:00 AM - 7:30 PM",
            "Bajrang Motors Mahindra Haldwani"
        ),
        (
            "Mahindra",
            "Kumar Autowheels",
            "kumar-autowheels-mahindra-rudrapur",
            "Rudrapur",
            "UK-06",
            "Delhi - Nainital Highway (NH-109), Near Metropolis Mall, Rudrapur, Uttarakhand 263153",
            "+91 5944 245 880",
            "919837167890",
            "Harish Joshi (Branch Manager)",
            4.8,
            280,
            "9:00 AM - 7:30 PM",
            "Kumar Autowheels Mahindra Rudrapur"
        ),

        # Hyundai
        (
            "Hyundai",
            "Sachin Hyundai",
            "sachin-hyundai-haldwani",
            "Haldwani",
            "UK-04",
            "Nainital Road, Near Tikonia, Haldwani, Uttarakhand 263139",
            "+91 5946 250 333",
            "919837012342",
            "Sunil Pandey (Manager)",
            4.8,
            310,
            "9:30 AM - 7:30 PM",
            "Sachin Hyundai Haldwani"
        ),
        (
            "Hyundai",
            "Bindal Hyundai",
            "bindal-hyundai-rudrapur",
            "Rudrapur",
            "UK-06",
            "Kichha Road, Opposite District Hospital, Rudrapur, Uttarakhand 263153",
            "+91 5944 252 800",
            "919837167892",
            "Vipin Chandra (GM)",
            4.7,
            240,
            "9:30 AM - 7:00 PM",
            "Bindal Hyundai Rudrapur"
        ),

        # Kia
        (
            "Kia",
            "Classic Kia",
            "classic-kia-haldwani",
            "Haldwani",
            "UK-04",
            "Kaladhungi Road, Near Kusumkhera, Haldwani, Uttarakhand 263139",
            "+91 5946 261 500",
            "919837012343",
            "Mohit Tiwari (Sales Lead)",
            4.9,
            275,
            "9:30 AM - 7:30 PM",
            "Classic Kia Haldwani"
        ),
        (
            "Kia",
            "Classic Kia",
            "classic-kia-rudrapur",
            "Rudrapur",
            "UK-06",
            "Kashipur Bypass, Near Big Bazaar Chowk, Rudrapur, Uttarakhand 263153",
            "+91 5944 260 112",
            "919837167893",
            "Deepak Bhatt (Showroom Incharge)",
            4.8,
            220,
            "9:30 AM - 7:00 PM",
            "Classic Kia Rudrapur"
        ),

        # Toyota
        (
            "Toyota",
            "Trust Toyota",
            "trust-toyota-haldwani",
            "Haldwani",
            "UK-04",
            "Rampur Road, Near ITI, Haldwani, Uttarakhand 263139",
            "+91 5946 280 900",
            "919837012344",
            "Girish Pathak (Sales Manager)",
            4.9,
            390,
            "9:00 AM - 7:30 PM",
            "Trust Toyota Haldwani"
        ),
        (
            "Toyota",
            "Trust Toyota",
            "trust-toyota-rudrapur",
            "Rudrapur",
            "UK-06",
            "NH-109, Opp. Radisson Blu Hotel, Rudrapur, Uttarakhand 263153",
            "+91 5944 270 450",
            "919837167894",
            "Arun Chauhan (Branch Head)",
            4.8,
            260,
            "9:00 AM - 7:00 PM",
            "Trust Toyota Rudrapur"
        ),

        # Maruti Suzuki
        (
            "Maruti Suzuki",
            "Nanital Moters",
            "nanital-moters-maruti-haldwani",
            "Haldwani",
            "UK-04",
            "Bareilly Road, Motahaldu, Haldwani, Uttarakhand 263139",
            "+91 5946 235 600",
            "919837012346",
            "Ramesh Danu (Sales Head)",
            4.8,
            420,
            "9:00 AM - 8:00 PM",
            "Nanital Moters Maruti Haldwani"
        ),
        (
            "Maruti Suzuki",
            "Akansha Automobiles",
            "akansha-automobiles-maruti-rudrapur",
            "Rudrapur",
            "UK-06",
            "Kashipur Road, Near Transit Camp, Rudrapur, Uttarakhand 263153",
            "+91 5944 246 700",
            "919837167895",
            "Kailash Upadhyay (General Manager)",
            4.7,
            380,
            "9:00 AM - 8:00 PM",
            "Akansha Automobiles Maruti Rudrapur"
        )
    ]

    for d in dealerships_data:
        cursor.execute("""
        INSERT INTO dealerships (brand, name, slug, city, rto_code, address, phone, whatsapp, manager_name, rating, reviews_count, timings, map_embed_query)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, d)

    # 2. Insert Popular Models across all 6 Brands
    # (make, model, slug, tagline, category, price_range, min_price, max_price, hero_image, fuel_types, transmissions, popular_choice)
    cars_data = [
        # Tata Motors
        ("Tata Motors", "Tata Nexon", "tata-nexon", "India's Safest SUV", "Subcompact SUV", "₹ 8.00 - 15.50 Lakh", 800000, 1550000, "", "Petrol, Diesel, CNG", "Manual, Automatic", 1),
        ("Tata Motors", "Tata Punch", "tata-punch", "The Urban Adventurer", "Micro SUV", "₹ 6.13 - 10.20 Lakh", 613000, 1020000, "", "Petrol, CNG", "Manual, Automatic", 1),
        ("Tata Motors", "Tata Curvv", "tata-curvv", "The Shifting Paradigm", "Coupe SUV", "₹ 10.00 - 19.00 Lakh", 1000000, 1900000, "", "Petrol, Diesel", "Manual, Automatic", 1),
        ("Tata Motors", "Tata Harrier", "tata-harrier", "Born of Pedigree", "Mid-size SUV", "₹ 15.49 - 26.44 Lakh", 1549000, 2644000, "", "Diesel", "Manual, Automatic", 1),

        # Mahindra
        ("Mahindra", "Mahindra Thar Roxx", "mahindra-thar-roxx", "5-Door Off-road Icon", "Mid-size SUV", "₹ 12.99 - 22.49 Lakh", 1299000, 2249000, "", "Diesel, Petrol", "Manual, Automatic", 1),
        ("Mahindra", "Mahindra Scorpio-N", "mahindra-scorpio-n", "Big Daddy of SUVs", "D-Segment SUV", "₹ 13.85 - 24.54 Lakh", 1385000, 2454000, "", "Diesel, Petrol", "Manual, Automatic", 1),
        ("Mahindra", "Mahindra XUV700", "mahindra-xuv700", "Intelligent Luxury", "Premium SUV", "₹ 13.99 - 26.49 Lakh", 1399000, 2649000, "", "Petrol, Diesel", "Manual, Automatic", 1),
        ("Mahindra", "Mahindra XUV 3XO", "mahindra-xuv-3xo", "Next-gen Disruptor", "Compact SUV", "₹ 7.79 - 15.49 Lakh", 779000, 1549000, "", "Petrol, Diesel", "Manual, Automatic", 1),
        ("Mahindra", "Mahindra Thar", "mahindra-thar", "Pure Off-roader", "Lifestyle 4x4", "₹ 11.35 - 17.60 Lakh", 1135000, 1760000, "", "Diesel, Petrol", "Manual, Automatic", 1),
        ("Mahindra", "Mahindra Bolero", "mahindra-bolero", "Undisputed Workhorse", "Utility SUV", "₹ 9.79 - 10.90 Lakh", 979000, 1090000, "", "Diesel", "Manual", 0),

        # Hyundai
        ("Hyundai", "Hyundai Creta", "hyundai-creta", "The Undisputed King", "Mid-size SUV", "₹ 11.00 - 20.15 Lakh", 1100000, 2015000, "", "Petrol, Diesel", "Manual, Automatic", 1),
        ("Hyundai", "Hyundai Venue", "hyundai-venue", "Lit SUV", "Compact SUV", "₹ 7.94 - 13.48 Lakh", 794000, 1348000, "", "Petrol, Diesel", "Manual, Automatic", 1),
        ("Hyundai", "Hyundai Exter", "hyundai-exter", "Think Outside", "Micro SUV", "₹ 6.13 - 10.28 Lakh", 613000, 1028000, "", "Petrol, CNG", "Manual, Automatic", 1),
        ("Hyundai", "Hyundai Verna", "hyundai-verna", "Futuristic Sedan", "Premium Sedan", "₹ 11.00 - 17.42 Lakh", 1100000, 1742000, "", "Petrol", "Manual, Automatic", 0),

        # Kia
        ("Kia", "Kia Seltos", "kia-seltos", "Badass by Nature", "Mid-size SUV", "₹ 10.90 - 20.35 Lakh", 1090000, 2035000, "", "Petrol, Diesel", "Manual, Automatic", 1),
        ("Kia", "Kia Sonet", "kia-sonet", "The Wild One", "Compact SUV", "₹ 7.99 - 15.75 Lakh", 799000, 1575000, "", "Petrol, Diesel", "Manual, Automatic", 1),
        ("Kia", "Kia Carens", "kia-carens", "The Space Mover", "MPV", "₹ 10.52 - 19.67 Lakh", 1052000, 1967000, "", "Petrol, Diesel", "Manual, Automatic", 1),

        # Toyota
        ("Toyota", "Toyota Urban Cruiser Hyryder", "toyota-urban-cruiser-hyryder", "Hybrid Tech Pioneer", "Mid-size SUV", "₹ 11.14 - 20.19 Lakh", 1114000, 2019000, "", "Petrol, Hybrid, CNG", "Manual, Automatic", 1),
        ("Toyota", "Toyota Innova Hycross", "toyota-innova-hycross", "Luxury Redefined", "Premium MPV", "₹ 19.77 - 30.98 Lakh", 1977000, 3098000, "", "Petrol, Hybrid", "Automatic", 1),
        ("Toyota", "Toyota Fortuner", "toyota-fortuner", "Leader of the Pack", "Full-size SUV", "₹ 33.43 - 51.44 Lakh", 3343000, 5144000, "", "Diesel, Petrol", "Manual, Automatic", 1),
        ("Toyota", "Toyota Glanza", "toyota-glanza", "Hatchin' Cool", "Premium Hatchback", "₹ 6.86 - 10.00 Lakh", 686000, 1000000, "", "Petrol, CNG", "Manual, Automatic", 0),

        # Maruti Suzuki
        ("Maruti Suzuki", "Maruti Suzuki Brezza", "maruti-suzuki-brezza", "Hot & Techy SUV", "Compact SUV", "₹ 8.34 - 14.14 Lakh", 834000, 1414000, "", "Petrol, CNG", "Manual, Automatic", 1),
        ("Maruti Suzuki", "Maruti Suzuki Grand Vitara", "maruti-suzuki-grand-vitara", "Strong Hybrid SUV", "Mid-size SUV", "₹ 10.87 - 20.09 Lakh", 1087000, 2009000, "", "Petrol, Hybrid, CNG", "Manual, Automatic", 1),
        ("Maruti Suzuki", "Maruti Suzuki Swift", "maruti-suzuki-swift", "Epic New Swift", "Hatchback", "₹ 6.49 - 9.64 Lakh", 649000, 964000, "", "Petrol, CNG", "Manual, Automatic", 1),
        ("Maruti Suzuki", "Maruti Suzuki Baleno", "maruti-suzuki-baleno", "Sensual Opulence", "Premium Hatchback", "₹ 6.66 - 9.88 Lakh", 666000, 988000, "", "Petrol, CNG", "Manual, Automatic", 1),
        ("Maruti Suzuki", "Maruti Suzuki Fronx", "maruti-suzuki-fronx", "Shape of New", "Compact Crossover", "₹ 7.51 - 13.04 Lakh", 751000, 1304000, "", "Petrol, CNG", "Manual, Automatic", 1),
        ("Maruti Suzuki", "Maruti Suzuki Dzire", "maruti-suzuki-dzire", "All New Sedan", "Compact Sedan", "₹ 6.79 - 10.14 Lakh", 679000, 1014000, "", "Petrol, CNG", "Manual, Automatic", 1)
    ]

    for c in cars_data:
        cursor.execute("""
        INSERT INTO cars (make, model, slug, tagline, category, price_range, min_price, max_price, hero_image, fuel_types, transmissions, popular_choice)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, c)

    cursor.execute("SELECT id, slug FROM cars;")
    car_ids = {row["slug"]: row["id"] for row in cursor.fetchall()}

    cursor.execute("SELECT id, slug FROM dealerships;")
    dealer_ids = {row["slug"]: row["id"] for row in cursor.fetchall()}

    # 3. Insert Trims & Variants
    variants_data = [
        # Tata
        (car_ids["tata-nexon"], "Creative Plus", "Petrol", "Manual", "FWD", "5-Seater", "1.2L Turbo Revotron", 1170000, "10.25-inch Touchscreen, 360 Camera, Wireless Android Auto"),
        (car_ids["tata-nexon"], "Fearless Plus S", "Diesel", "Automatic", "FWD", "5-Seater", "1.5L Revotorq", 1490000, "Ventilated Seats, Sunroof, JBL Sound System"),
        (car_ids["tata-punch"], "Accomplished Dazzle", "Petrol", "Manual", "FWD", "5-Seater", "1.2L Revotron", 825000, "Harman Infotainment, 16-inch Diamond Cut Alloys"),
        (car_ids["tata-curvv"], "Accomplished Plus A", "Diesel", "Automatic", "FWD", "5-Seater", "1.5L Kryojet", 1750000, "Level 2 ADAS, Panoramic Sunroof, Gesture Tailgate"),
        (car_ids["tata-harrier"], "Adventure Plus A", "Diesel", "Automatic", "FWD", "5-Seater", "2.0L Kryotec", 2250000, "Panoramic Sunroof, ADAS, 12.3-inch Display"),

        # Mahindra
        (car_ids["mahindra-thar-roxx"], "AX7 L 4x4", "Diesel", "Automatic", "4x4", "5-Seater", "2.2L mHawk", 2249000, "Level 2 ADAS, Ventilated Seats, Harman Kardon Sound"),
        (car_ids["mahindra-thar-roxx"], "MX3", "Diesel", "Manual", "RWD", "5-Seater", "2.2L mHawk", 1599000, "10.25-inch Screen, Wireless Android Auto, Rear AC"),
        (car_ids["mahindra-scorpio-n"], "Z8 L", "Diesel", "Automatic", "4x4", "7-Seater", "2.2L mHawk", 2299000, "Sony 12-Speaker Sound, 4XPLOR Modes, Wireless Charger"),
        (car_ids["mahindra-scorpio-n"], "Z4 Diesel MT", "Diesel", "Manual", "2WD", "7-Seater", "2.2L mHawk", 1595000, "Rear AC, Touchscreen, ESP, Hill Hold"),
        (car_ids["mahindra-xuv700"], "AX7 L 7-Seater", "Petrol", "Automatic", "2WD", "7-Seater", "2.0L mStallion", 2649000, "Level 2 ADAS, Sony 3D Audio, 360 Camera, Panoramic Sunroof"),
        (car_ids["mahindra-xuv-3xo"], "AX5", "Petrol", "Manual", "FWD", "5-Seater", "1.2L Turbo", 1149000, "Panoramic Skyroof, Dual Zone Climate, 10.25-inch Display"),
        (car_ids["mahindra-thar"], "LX 4x4 Hard Top", "Diesel", "Manual", "4x4", "4-Seater", "2.2L mHawk", 1699000, "Mechanical Locking Diff, Deep Silver Alloys, Touchscreen"),
        (car_ids["mahindra-bolero"], "B6 (O)", "Diesel", "Manual", "RWD", "7-Seater", "1.5L mHawk75", 979000, "Driver Airbag, ABS with EBD, Bluetooth"),

        # Hyundai
        (car_ids["hyundai-creta"], "SX (O) Turbo", "Petrol", "Automatic", "FWD", "5-Seater", "1.5L Turbo GDi", 2015000, "Level 2 ADAS, Dual Zone Climate, Bose 8-Speaker Sound"),
        (car_ids["hyundai-creta"], "S (O)", "Diesel", "Manual", "FWD", "5-Seater", "1.5L U2 CRDi", 1436000, "Panoramic Sunroof, LED Headlamps, Wireless Charger"),
        (car_ids["hyundai-venue"], "SX (O)", "Petrol", "Automatic", "FWD", "5-Seater", "1.0L Turbo GDi", 1320000, "Connected Car Tech, Sunroof, Air Purifier"),
        (car_ids["hyundai-exter"], "SX", "Petrol", "Manual", "FWD", "5-Seater", "1.2L Kappa", 823000, "Electric Sunroof, Dashcam with Dual Camera"),

        # Kia
        (car_ids["kia-seltos"], "HTX Plus", "Diesel", "Automatic", "FWD", "5-Seater", "1.5L CRDi VGT", 1870000, "Panoramic Sunroof, Bose Sound, Ventilated Seats"),
        (car_ids["kia-seltos"], "HTK Plus", "Petrol", "Manual", "FWD", "5-Seater", "1.5L Smartstream", 1259000, "Touchscreen Infotainment, Alloys, Push Button Start"),
        (car_ids["kia-sonet"], "HTX", "Diesel", "Automatic", "FWD", "5-Seater", "1.5L CRDi", 1310000, "Sunroof, LED Headlamps, Drive Modes"),
        (car_ids["kia-carens"], "Prestige Plus", "Diesel", "Manual", "FWD", "7-Seater", "1.5L CRDi", 1520000, "Auto AC, 16-inch Alloys, Keyless Entry"),

        # Toyota
        (car_ids["toyota-urban-cruiser-hyryder"], "G Strong Hybrid", "Hybrid", "Automatic", "FWD", "5-Seater", "1.5L TNGA Petrol Hybrid", 1879000, "Head-up Display, 9-inch Smart Playcast, EV Mode"),
        (car_ids["toyota-urban-cruiser-hyryder"], "S NeoDrive", "Petrol", "Manual", "FWD", "5-Seater", "1.5L K-Series", 1281000, "Touchscreen, Cruise Control, Projector Lamps"),
        (car_ids["toyota-innova-hycross"], "ZX (O) Hybrid", "Hybrid", "Automatic", "FWD", "7-Seater", "2.0L TNGA Hybrid", 3098000, "Ottoman Captain Seats, Panoramic Roof, Toyota Safety Sense"),
        (car_ids["toyota-fortuner"], "4x4 AT", "Diesel", "Automatic", "4x4", "7-Seater", "2.8L Diesel", 4232000, "Differential Lock, JBL Audio, Connected Features"),
        (car_ids["toyota-glanza"], "G", "Petrol", "Manual", "FWD", "5-Seater", "1.2L K-Series", 878000, "Smartplay Cast Touchscreen, LED Projectors, Alloys"),

        # Maruti Suzuki
        (car_ids["maruti-suzuki-brezza"], "ZXi Plus", "Petrol", "Automatic", "FWD", "5-Seater", "1.5L K15C", 1398000, "360 View Camera, Head-Up Display, Sunroof"),
        (car_ids["maruti-suzuki-brezza"], "VXi", "Petrol", "Manual", "FWD", "5-Seater", "1.5L K15C", 969000, "7-inch Touchscreen, Auto Climate Control, ESP"),
        (car_ids["maruti-suzuki-grand-vitara"], "Alpha Strong Hybrid", "Hybrid", "Automatic", "FWD", "5-Seater", "1.5L Intelligent Hybrid", 1999000, "Panoramic Sunroof, Ventilated Seats, 360 Camera"),
        (car_ids["maruti-suzuki-grand-vitara"], "Zeta", "Petrol", "Manual", "FWD", "5-Seater", "1.5L K15C", 1391000, "Smartplay Pro+, 6 Airbags, LED Projectors"),
        (car_ids["maruti-suzuki-swift"], "ZXi Plus", "Petrol", "Manual", "FWD", "5-Seater", "1.2L Z-Series", 900000, "9-inch Touchscreen, LED DRLs, Wireless Charger"),
        (car_ids["maruti-suzuki-baleno"], "Alpha", "Petrol", "Automatic", "FWD", "5-Seater", "1.2L DualJet", 988000, "Head Up Display, 360 Camera, 9-inch SmartPlay"),
        (car_ids["maruti-suzuki-fronx"], "Alpha Turbo", "Petrol", "Automatic", "FWD", "5-Seater", "1.0L Boosterjet", 1298000, "Paddle Shifters, HUD, 360 Camera"),
        (car_ids["maruti-suzuki-dzire"], "ZXi Plus", "Petrol", "Manual", "FWD", "5-Seater", "1.2L Z-Series", 969000, "Sunroof, 360 Camera, 6 Airbags standard")
    ]

    for v in variants_data:
        cursor.execute("""
        INSERT INTO variants (car_id, name, fuel_type, transmission, drivetrain, seating, engine_spec, ex_showroom_price, key_features)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, v)

    # Re-fetch variant map by (car_id, name) to prevent collision of names like ZXi Plus
    cursor.execute("SELECT id, car_id, name FROM variants;")
    v_rows = cursor.fetchall()
    v_map = {}
    for r in v_rows:
        v_map[(r["car_id"], r["name"])] = r["id"]

    # 4. Insert Authentic Inventory across all 12 Dealerships (Haldwani & Rudrapur)
    inventory_data = [
        # TATA MOTORS - Haldwani: Gola Ganapati Motors
        (dealer_ids["gola-ganapati-tata-haldwani"], v_map[(car_ids["tata-nexon"], "Creative Plus")], "IN_STOCK", 3, 0, "Calgary White, Daytona Grey", 1, "Ready showroom units in Haldwani."),
        (dealer_ids["gola-ganapati-tata-haldwani"], v_map[(car_ids["tata-punch"], "Accomplished Dazzle")], "IN_STOCK", 2, 0, "Atomic Orange, Foliage Green", 1, "Immediate delivery with festive discount."),
        (dealer_ids["gola-ganapati-tata-haldwani"], v_map[(car_ids["tata-curvv"], "Accomplished Plus A")], "IN_TRANSIT", 1, 1, "Pristine White", 1, "Arriving this weekend in Haldwani."),

        # TATA MOTORS - Rudrapur: Amit Auto
        (dealer_ids["amit-auto-tata-rudrapur"], v_map[(car_ids["tata-nexon"], "Fearless Plus S")], "IN_STOCK", 2, 0, "Fearless Purple", 1, "Ready stock at Rudrapur showroom."),
        (dealer_ids["amit-auto-tata-rudrapur"], v_map[(car_ids["tata-harrier"], "Adventure Plus A")], "IN_STOCK", 1, 0, "Sunlit Yellow", 1, "Immediate test drive and delivery."),
        (dealer_ids["amit-auto-tata-rudrapur"], v_map[(car_ids["tata-punch"], "Accomplished Dazzle")], "IN_STOCK", 2, 0, "Tropical Mist", 1, "Ready stock with UK-06 registration."),

        # MAHINDRA - Haldwani: Bajrang Motors
        (dealer_ids["bajrang-motors-mahindra-haldwani"], v_map[(car_ids["mahindra-thar-roxx"], "AX7 L 4x4")], "IN_STOCK", 2, 0, "Stealth Black, Everest White", 1, "Ready floor units in Haldwani."),
        (dealer_ids["bajrang-motors-mahindra-haldwani"], v_map[(car_ids["mahindra-scorpio-n"], "Z8 L")], "IN_STOCK", 2, 0, "Napoli Black", 1, "Ready for delivery on Kathgodam highway."),
        (dealer_ids["bajrang-motors-mahindra-haldwani"], v_map[(car_ids["mahindra-xuv-3xo"], "AX5")], "IN_STOCK", 3, 0, "Tango Red", 1, "Immediate delivery."),
        (dealer_ids["bajrang-motors-mahindra-haldwani"], v_map[(car_ids["mahindra-thar"], "LX 4x4 Hard Top")], "IN_STOCK", 1, 0, "Red Rage", 1, "Off-road demo unit and fresh stock available."),

        # MAHINDRA - Rudrapur: Kumar Autowheels
        (dealer_ids["kumar-autowheels-mahindra-rudrapur"], v_map[(car_ids["mahindra-thar-roxx"], "MX3")], "IN_STOCK", 2, 0, "Deep Forest", 1, "Ready stock at Metropolis Mall outlet."),
        (dealer_ids["kumar-autowheels-mahindra-rudrapur"], v_map[(car_ids["mahindra-scorpio-n"], "Z4 Diesel MT")], "IN_STOCK", 2, 0, "Dazzling Silver", 1, "Ready delivery in Rudrapur."),
        (dealer_ids["kumar-autowheels-mahindra-rudrapur"], v_map[(car_ids["mahindra-bolero"], "B6 (O)")], "IN_STOCK", 3, 0, "Diamond White", 1, "Commercial and private ready stock."),

        # HYUNDAI - Haldwani: Sachin Hyundai
        (dealer_ids["sachin-hyundai-haldwani"], v_map[(car_ids["hyundai-creta"], "SX (O) Turbo")], "IN_STOCK", 2, 0, "Abyss Black, Ranger Khaki", 1, "Top model ready in showroom."),
        (dealer_ids["sachin-hyundai-haldwani"], v_map[(car_ids["hyundai-venue"], "SX (O)")], "IN_STOCK", 2, 0, "Titan Grey", 1, "Ready delivery on Nainital Road."),
        (dealer_ids["sachin-hyundai-haldwani"], v_map[(car_ids["hyundai-exter"], "SX")], "IN_TRANSIT", 2, 1, "Atlas White", 1, "Arriving in 3 days."),

        # HYUNDAI - Rudrapur: Bindal Hyundai
        (dealer_ids["bindal-hyundai-rudrapur"], v_map[(car_ids["hyundai-creta"], "S (O)")], "IN_STOCK", 2, 0, "Robust Emerald Pearl", 1, "Ready stock on Kichha Road showroom."),
        (dealer_ids["bindal-hyundai-rudrapur"], v_map[(car_ids["hyundai-creta"], "SX (O) Turbo")], "IN_TRANSIT", 1, 1, "Fiery Red", 1, "Allotted unit arriving Friday."),

        # KIA - Haldwani: Classic Kia
        (dealer_ids["classic-kia-haldwani"], v_map[(car_ids["kia-seltos"], "HTX Plus")], "IN_STOCK", 2, 0, "Pewter Olive, Glacier White", 1, "Immediate delivery in Haldwani."),
        (dealer_ids["classic-kia-haldwani"], v_map[(car_ids["kia-sonet"], "HTX")], "IN_STOCK", 2, 0, "Aurora Black Pearl", 1, "Ready test drive and delivery."),

        # KIA - Rudrapur: Classic Kia
        (dealer_ids["classic-kia-rudrapur"], v_map[(car_ids["kia-seltos"], "HTK Plus")], "IN_STOCK", 2, 0, "Gravity Grey", 1, "Ready units on Kashipur bypass showroom."),
        (dealer_ids["classic-kia-rudrapur"], v_map[(car_ids["kia-carens"], "Prestige Plus")], "IN_STOCK", 1, 0, "Imperial Blue", 1, "7-seater ready for immediate delivery."),

        # TOYOTA - Haldwani: Trust Toyota
        (dealer_ids["trust-toyota-haldwani"], v_map[(car_ids["toyota-urban-cruiser-hyryder"], "G Strong Hybrid")], "IN_STOCK", 2, 0, "Cafe White, Gaming Grey", 1, "High efficiency hybrid ready on Rampur Road."),
        (dealer_ids["trust-toyota-haldwani"], v_map[(car_ids["toyota-fortuner"], "4x4 AT")], "IN_STOCK", 1, 0, "Attitude Black", 1, "Ready Fortuner unit in stockyard."),
        (dealer_ids["trust-toyota-haldwani"], v_map[(car_ids["toyota-glanza"], "G")], "IN_STOCK", 2, 0, "Sporting Red", 1, "Ready stock."),

        # TOYOTA - Rudrapur: Trust Toyota
        (dealer_ids["trust-toyota-rudrapur"], v_map[(car_ids["toyota-innova-hycross"], "ZX (O) Hybrid")], "IN_STOCK", 1, 0, "Blackish Ageha Glass Flake", 1, "Showroom floor unit ready for immediate delivery."),
        (dealer_ids["trust-toyota-rudrapur"], v_map[(car_ids["toyota-urban-cruiser-hyryder"], "S NeoDrive")], "IN_STOCK", 2, 0, "Super White", 1, "Ready stock with UK-06 registration."),

        # MARUTI SUZUKI - Haldwani: Nanital Moters
        (dealer_ids["nanital-moters-maruti-haldwani"], v_map[(car_ids["maruti-suzuki-brezza"], "ZXi Plus")], "IN_STOCK", 3, 0, "Magma Grey, Pearl Arctic White", 1, "Ready stock in Haldwani Motahaldu showroom."),
        (dealer_ids["nanital-moters-maruti-haldwani"], v_map[(car_ids["maruti-suzuki-grand-vitara"], "Alpha Strong Hybrid")], "IN_STOCK", 2, 0, "Nexa Blue, Grandeur Grey", 1, "Strong Hybrid ready for fast delivery."),
        (dealer_ids["nanital-moters-maruti-haldwani"], v_map[(car_ids["maruti-suzuki-swift"], "ZXi Plus")], "IN_STOCK", 4, 0, "Luster Blue, Sizzling Red", 1, "New Swift top variant ready."),

        # MARUTI SUZUKI - Rudrapur: Akansha Automobiles
        (dealer_ids["akansha-automobiles-maruti-rudrapur"], v_map[(car_ids["maruti-suzuki-brezza"], "VXi")], "IN_STOCK", 3, 0, "Brave Khaki, Splendid Silver", 1, "Ready stock on Kashipur Road."),
        (dealer_ids["akansha-automobiles-maruti-rudrapur"], v_map[(car_ids["maruti-suzuki-grand-vitara"], "Zeta")], "IN_STOCK", 2, 0, "Splendid Silver", 1, "Ready units for immediate registration."),
        (dealer_ids["akansha-automobiles-maruti-rudrapur"], v_map[(car_ids["maruti-suzuki-fronx"], "Alpha Turbo")], "IN_STOCK", 2, 0, "Bluish Black", 1, "Turbo Fronx available on display.")
    ]

    for inv in inventory_data:
        cursor.execute("""
        INSERT INTO inventory (dealership_id, variant_id, status, units_available, waiting_period_weeks, colors_available, test_drive_available, promo_note)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """, inv)

    # 5. Seed Staff & Admin Accounts
    cursor.execute("DELETE FROM admin_users;")
    cursor.execute("DELETE FROM sessions;")
    
    from app.auth import hash_password

    admin_hash, admin_salt = hash_password("scoutmycar2026")
    staff_hash, staff_salt = hash_password("staff")

    admin_users = [
        ("admin", admin_hash, admin_salt, "System Administrator", "super_admin", None),
        ("tata_haldwani", staff_hash, staff_salt, "Gola Ganapati Motors Manager", "dealer_manager", dealer_ids["gola-ganapati-tata-haldwani"]),
        ("mahindra_haldwani", staff_hash, staff_salt, "Bajrang Motors Manager", "dealer_manager", dealer_ids["bajrang-motors-mahindra-haldwani"]),
        ("hyundai_haldwani", staff_hash, staff_salt, "Sachin Hyundai Manager", "dealer_manager", dealer_ids["sachin-hyundai-haldwani"]),
        ("kia_haldwani", staff_hash, staff_salt, "Classic Kia Haldwani Manager", "dealer_manager", dealer_ids["classic-kia-haldwani"]),
        ("toyota_haldwani", staff_hash, staff_salt, "Trust Toyota Haldwani Manager", "dealer_manager", dealer_ids["trust-toyota-haldwani"]),
        ("maruti_haldwani", staff_hash, staff_salt, "Nanital Moters Manager", "dealer_manager", dealer_ids["nanital-moters-maruti-haldwani"]),
        ("tata_rudrapur", staff_hash, staff_salt, "Amit Auto Manager", "dealer_manager", dealer_ids["amit-auto-tata-rudrapur"]),
        ("mahindra_rudrapur", staff_hash, staff_salt, "Kumar Autowheels Manager", "dealer_manager", dealer_ids["kumar-autowheels-mahindra-rudrapur"]),
        ("hyundai_rudrapur", staff_hash, staff_salt, "Bindal Hyundai Manager", "dealer_manager", dealer_ids["bindal-hyundai-rudrapur"]),
        ("kia_rudrapur", staff_hash, staff_salt, "Classic Kia Rudrapur Manager", "dealer_manager", dealer_ids["classic-kia-rudrapur"]),
        ("toyota_rudrapur", staff_hash, staff_salt, "Trust Toyota Rudrapur Manager", "dealer_manager", dealer_ids["trust-toyota-rudrapur"]),
        ("maruti_rudrapur", staff_hash, staff_salt, "Akansha Automobiles Manager", "dealer_manager", dealer_ids["akansha-automobiles-maruti-rudrapur"])
    ]

    for u in admin_users:
        cursor.execute("""
        INSERT INTO admin_users (username, password_hash, salt, name, role, dealership_id)
        VALUES (?, ?, ?, ?, ?, ?);
        """, u)

    conn.commit()
    conn.close()
    print("Database seeded with 12 authorized dealerships across 6 brands (Tata, Mahindra, Hyundai, Kia, Toyota, Maruti Suzuki) for Haldwani & Rudrapur!")

if __name__ == "__main__":
    seed()
