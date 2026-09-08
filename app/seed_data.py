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

    # 1. Insert 12 Dealerships across 6 Brands in Haldwani & Rudrapur (Clean city names, no RTO codes in text)
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

        # Maruti Suzuki (Nanital Moters in Haldwani, Akansha Automobiles in Rudrapur)
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

    # 2. Insert Popular Models across all 6 OEMs
    cars_data = [
        # Tata Motors
        ("Tata Motors", "Tata Nexon", "tata-nexon", "India's Safest SUV", "Subcompact SUV", "₹ 8.00 - 15.50 Lakh", 800000, 1550000, "", "Petrol, Diesel, CNG, Electric", "Manual, Automatic, DCT", 1),
        ("Tata Motors", "Tata Punch", "tata-punch", "The Urban Adventurer", "Micro SUV", "₹ 6.13 - 10.20 Lakh", 613000, 1020000, "", "Petrol, CNG, Electric", "Manual, AMT, Automatic", 1),
        ("Tata Motors", "Tata Curvv", "tata-curvv", "The Shifting Paradigm", "Coupe SUV", "₹ 10.00 - 19.00 Lakh", 1000000, 1900000, "", "Petrol, Diesel, Electric", "Manual, DCT, Automatic", 1),
        ("Tata Motors", "Tata Harrier", "tata-harrier", "Born of Pedigree", "Mid-size SUV", "₹ 15.49 - 26.44 Lakh", 1549000, 2644000, "", "Diesel", "Manual, Automatic", 1),
        ("Tata Motors", "Tata Safari", "tata-safari", "The Flagship 7-Seater", "Premium SUV", "₹ 16.19 - 27.34 Lakh", 1619000, 2734000, "", "Diesel", "Manual, Automatic", 1),

        # Mahindra
        ("Mahindra", "Mahindra Thar Roxx", "mahindra-thar-roxx", "5-Door Off-road Icon", "Mid-size SUV", "₹ 12.99 - 22.49 Lakh", 1299000, 2249000, "", "Diesel, Petrol", "Manual, Automatic", 1),
        ("Mahindra", "Mahindra Scorpio-N", "mahindra-scorpio-n", "Big Daddy of SUVs", "D-Segment SUV", "₹ 13.85 - 24.54 Lakh", 1385000, 2454000, "", "Diesel, Petrol", "Manual, Automatic", 1),
        ("Mahindra", "Mahindra XUV700", "mahindra-xuv700", "Intelligent Luxury", "Premium SUV", "₹ 13.99 - 26.49 Lakh", 1399000, 2649000, "", "Petrol, Diesel", "Manual, Automatic", 1),
        ("Mahindra", "Mahindra XUV 3XO", "mahindra-xuv-3xo", "Next-gen Disruptor", "Compact SUV", "₹ 7.79 - 15.49 Lakh", 779000, 1549000, "", "Petrol, Diesel", "Manual, Automatic", 1),
        ("Mahindra", "Mahindra Thar", "mahindra-thar", "Pure Off-roader", "Lifestyle 4x4", "₹ 11.35 - 17.60 Lakh", 1135000, 1760000, "", "Diesel, Petrol", "Manual, Automatic", 1),
        ("Mahindra", "Mahindra Bolero", "mahindra-bolero", "Undisputed Workhorse", "Utility SUV", "₹ 9.79 - 10.90 Lakh", 979000, 1090000, "", "Diesel", "Manual", 1),

        # Hyundai
        ("Hyundai", "Hyundai Creta", "hyundai-creta", "The Undisputed King", "Mid-size SUV", "₹ 11.00 - 20.15 Lakh", 1100000, 2015000, "", "Petrol, Diesel", "Manual, IVT, DCT, Automatic", 1),
        ("Hyundai", "Hyundai Venue", "hyundai-venue", "Lit SUV", "Compact SUV", "₹ 7.94 - 13.48 Lakh", 794000, 1348000, "", "Petrol, Diesel, CNG", "Manual, DCT", 1),
        ("Hyundai", "Hyundai Exter", "hyundai-exter", "Think Outside", "Micro SUV", "₹ 6.13 - 10.28 Lakh", 613000, 1028000, "", "Petrol, CNG", "Manual, AMT", 1),
        ("Hyundai", "Hyundai Verna", "hyundai-verna", "Futuristic Sedan", "Premium Sedan", "₹ 11.00 - 17.42 Lakh", 1100000, 1742000, "", "Petrol", "Manual, IVT, DCT", 1),

        # Kia
        ("Kia", "Kia Seltos", "kia-seltos", "Badass by Nature", "Mid-size SUV", "₹ 10.90 - 20.35 Lakh", 1090000, 2035000, "", "Petrol, Diesel", "Manual, iMT, IVT, DCT, Automatic", 1),
        ("Kia", "Kia Sonet", "kia-sonet", "The Wild One", "Compact SUV", "₹ 7.99 - 15.75 Lakh", 799000, 1575000, "", "Petrol, Diesel", "Manual, iMT, DCT, Automatic", 1),
        ("Kia", "Kia Carens", "kia-carens", "The Space Mover", "MPV", "₹ 10.52 - 19.67 Lakh", 1052000, 1967000, "", "Petrol, Diesel", "Manual, iMT, DCT, Automatic", 1),

        # Toyota
        ("Toyota", "Toyota Urban Cruiser Hyryder", "toyota-urban-cruiser-hyryder", "Hybrid Tech Pioneer", "Mid-size SUV", "₹ 11.14 - 20.19 Lakh", 1114000, 2019000, "", "Petrol, Hybrid, CNG", "Manual, Automatic, e-CVT", 1),
        ("Toyota", "Toyota Innova Hycross", "toyota-innova-hycross", "Luxury Redefined", "Premium MPV", "₹ 19.77 - 30.98 Lakh", 1977000, 3098000, "", "Petrol, Hybrid", "Automatic, e-CVT", 1),
        ("Toyota", "Toyota Fortuner", "toyota-fortuner", "Leader of the Pack", "Full-size SUV", "₹ 33.43 - 51.44 Lakh", 3343000, 5144000, "", "Diesel, Petrol", "Manual, Automatic", 1),
        ("Toyota", "Toyota Glanza", "toyota-glanza", "Hatchin' Cool", "Premium Hatchback", "₹ 6.86 - 10.00 Lakh", 686000, 1000000, "", "Petrol, CNG", "Manual, AMT", 1),

        # Maruti Suzuki
        ("Maruti Suzuki", "Maruti Suzuki Brezza", "maruti-suzuki-brezza", "Hot & Techy SUV", "Compact SUV", "₹ 8.34 - 14.14 Lakh", 834000, 1414000, "", "Petrol, CNG", "Manual, Automatic", 1),
        ("Maruti Suzuki", "Maruti Suzuki Grand Vitara", "maruti-suzuki-grand-vitara", "Strong Hybrid SUV", "Mid-size SUV", "₹ 10.87 - 20.09 Lakh", 1087000, 2009000, "", "Petrol, Hybrid, CNG", "Manual, Automatic, e-CVT", 1),
        ("Maruti Suzuki", "Maruti Suzuki Swift", "maruti-suzuki-swift", "Epic New Swift", "Hatchback", "₹ 6.49 - 9.64 Lakh", 649000, 964000, "", "Petrol, CNG", "Manual, AMT", 1),
        ("Maruti Suzuki", "Maruti Suzuki Baleno", "maruti-suzuki-baleno", "Sensual Opulence", "Premium Hatchback", "₹ 6.66 - 9.88 Lakh", 666000, 988000, "", "Petrol, CNG", "Manual, AMT", 1),
        ("Maruti Suzuki", "Maruti Suzuki Fronx", "maruti-suzuki-fronx", "Shape of New", "Compact Crossover", "₹ 7.51 - 13.04 Lakh", 751000, 1304000, "", "Petrol, CNG", "Manual, AMT, Automatic", 1),
        ("Maruti Suzuki", "Maruti Suzuki Dzire", "maruti-suzuki-dzire", "All New Sedan", "Compact Sedan", "₹ 6.79 - 10.14 Lakh", 679000, 1014000, "", "Petrol, CNG", "Manual, AMT", 1)
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

    # 3. Insert Comprehensive Trims & Variants across Transmissions & Fuel Types
    variants_data = [
        # Tata Motors
        (car_ids["tata-nexon"], "Smart MT", "Petrol", "Manual", "FWD", "5-Seater", "1.2L Turbo Revotron", 800000, "6 Airbags Standard, LED DRLs, ESP"),
        (car_ids["tata-nexon"], "Creative Plus DCA", "Petrol", "DCT", "FWD", "5-Seater", "1.2L Turbo Revotron", 1170000, "10.25-inch Touchscreen, 360 Camera, Wireless Android Auto"),
        (car_ids["tata-nexon"], "Fearless Plus S Diesel AT", "Diesel", "Automatic", "FWD", "5-Seater", "1.5L Revotorq", 1490000, "Ventilated Seats, Sunroof, JBL Sound System"),
        (car_ids["tata-nexon"], "Creative iCNG", "CNG", "Manual", "FWD", "5-Seater", "1.2L Twin-Cylinder CNG", 1120000, "Twin Cylinder Boot Space, Panoramic Sunroof"),
        (car_ids["tata-nexon"], "Empowered Plus LR EV", "Electric", "Automatic", "FWD", "5-Seater", "Permanent Magnet AC Motor (45kWh)", 1699000, "465km Range, V2V & V2L Charging, Electronic Parking Brake"),
        (car_ids["tata-punch"], "Accomplished Dazzle MT", "Petrol", "Manual", "FWD", "5-Seater", "1.2L Revotron", 825000, "Harman Infotainment, 16-inch Diamond Cut Alloys"),
        (car_ids["tata-punch"], "Accomplished AMT", "Petrol", "AMT", "FWD", "5-Seater", "1.2L Revotron", 890000, "Traction Pro Mode, Auto Climate Control"),
        (car_ids["tata-punch"], "Adventure iCNG", "CNG", "Manual", "FWD", "5-Seater", "1.2L Bi-Fuel CNG", 795000, "Twin Cylinder Technology, High Usable Boot"),
        (car_ids["tata-curvv"], "Creative S Petrol DCA", "Petrol", "DCT", "FWD", "5-Seater", "1.2L Hyperion GDi", 1270000, "Dual Clutch DCA, Paddle Shifters, 10.25-inch Display"),
        (car_ids["tata-curvv"], "Accomplished Plus A Diesel AT", "Diesel", "Automatic", "FWD", "5-Seater", "1.5L Kryojet", 1750000, "Level 2 ADAS, Panoramic Sunroof, Gesture Tailgate"),
        (car_ids["tata-harrier"], "Adventure Plus A AT", "Diesel", "Automatic", "FWD", "5-Seater", "2.0L Kryotec", 2250000, "Panoramic Sunroof, ADAS, 12.3-inch Display, Terrain Modes"),
        (car_ids["tata-harrier"], "Pure MT", "Diesel", "Manual", "FWD", "5-Seater", "2.0L Kryotec", 1699000, "Touchscreen, Digital Instrument Cluster, ESP"),
        (car_ids["tata-safari"], "Accomplished Plus 6-Str AT", "Diesel", "Automatic", "FWD", "6-Seater", "2.0L Kryotec", 2650000, "Captain Seats with Ventilation, Boss Mode, ADAS"),

        # Mahindra
        (car_ids["mahindra-thar-roxx"], "MX3 Petrol MT", "Petrol", "Manual", "RWD", "5-Seater", "2.0L mStallion", 1499000, "10.25-inch Screen, Wireless Android Auto, Rear AC"),
        (car_ids["mahindra-thar-roxx"], "AX5 L Diesel AT", "Diesel", "Automatic", "RWD", "5-Seater", "2.2L mHawk", 1899000, "Level 2 ADAS, Wireless Charger, Electronic Parking Brake"),
        (car_ids["mahindra-thar-roxx"], "AX7 L 4x4 Diesel AT", "Diesel", "Automatic", "4x4", "5-Seater", "2.2L mHawk", 2249000, "Level 2 ADAS, Ventilated Seats, Harman Kardon Sound, Panoramic Sunroof"),
        (car_ids["mahindra-scorpio-n"], "Z4 Diesel MT", "Diesel", "Manual", "2WD", "7-Seater", "2.2L mHawk", 1595000, "Rear AC, Touchscreen, ESP, Hill Hold Control"),
        (car_ids["mahindra-scorpio-n"], "Z8 L Diesel AT 4x4", "Diesel", "Automatic", "4x4", "7-Seater", "2.2L mHawk", 2299000, "Sony 12-Speaker 3D Sound, 4XPLOR Modes, Wireless Charger"),
        (car_ids["mahindra-scorpio-n"], "Z8 Petrol AT", "Petrol", "Automatic", "2WD", "7-Seater", "2.0L mStallion", 2049000, "Sunroof, Coffee Black Leatherette, Dual Zone AC"),
        (car_ids["mahindra-xuv700"], "AX7 L 7-Str Petrol AT", "Petrol", "Automatic", "2WD", "7-Seater", "2.0L mStallion", 2449000, "Level 2 ADAS, Sony 3D Audio, 360 Camera, Panoramic Skyroof"),
        (car_ids["mahindra-xuv700"], "AX7 Diesel AT AWD", "Diesel", "Automatic", "AWD", "7-Seater", "2.2L mHawk", 2599000, "All Wheel Drive, Dual 10.25-inch Screens, Memory Seat"),
        (car_ids["mahindra-xuv-3xo"], "AX5 Petrol AT", "Petrol", "Automatic", "FWD", "5-Seater", "1.2L Turbo", 1249000, "6-Speed AISIN Automatic, Dual Zone Climate, Skyroof"),
        (car_ids["mahindra-xuv-3xo"], "AX7 L Diesel MT", "Diesel", "Manual", "FWD", "5-Seater", "1.5L Turbo Diesel", 1499000, "Level 2 ADAS, 360 Camera, Blind View Monitor"),
        (car_ids["mahindra-thar"], "LX 4x4 Hard Top Diesel MT", "Diesel", "Manual", "4x4", "4-Seater", "2.2L mHawk", 1699000, "Mechanical Locking Differential, Touchscreen, Washable Floor"),
        (car_ids["mahindra-thar"], "LX 4x4 Hard Top Petrol AT", "Petrol", "Automatic", "4x4", "4-Seater", "2.0L mStallion", 1760000, "Torque Converter Automatic, 18-inch Alloys, ESP"),
        (car_ids["mahindra-bolero"], "B6 (O) Diesel MT", "Diesel", "Manual", "RWD", "7-Seater", "1.5L mHawk75", 979000, "Micro Hybrid Tech, Driver Airbag, ABS with EBD"),

        # Hyundai
        (car_ids["hyundai-creta"], "EX Diesel MT", "Diesel", "Manual", "FWD", "5-Seater", "1.5L U2 CRDi", 1225000, "8-inch Touchscreen, Steering Audio Controls, 6 Airbags"),
        (car_ids["hyundai-creta"], "S (O) Petrol IVT", "Petrol", "IVT", "FWD", "5-Seater", "1.5L MPi", 1586000, "Panoramic Sunroof, LED Headlamps, Drive Modes"),
        (car_ids["hyundai-creta"], "SX (O) Turbo Petrol DCT", "Petrol", "DCT", "FWD", "5-Seater", "1.5L Turbo GDi", 2015000, "Level 2 ADAS, Dual Zone Climate, Bose 8-Speaker Sound"),
        (car_ids["hyundai-creta"], "SX (O) Diesel AT", "Diesel", "Automatic", "FWD", "5-Seater", "1.5L U2 CRDi", 2000000, "Ventilated Front Seats, 360 Camera, 8-Way Powered Seat"),
        (car_ids["hyundai-venue"], "SX (O) Turbo DCT", "Petrol", "DCT", "FWD", "5-Seater", "1.0L Turbo GDi", 1320000, "Connected Car Tech, Sunroof, Air Purifier, Paddle Shifters"),
        (car_ids["hyundai-venue"], "S (O) Plus CNG", "CNG", "Manual", "FWD", "5-Seater", "1.2L Bi-Fuel CNG", 935000, "Electric Sunroof, 8-inch Display, High Fuel Efficiency"),
        (car_ids["hyundai-venue"], "SX Diesel MT", "Diesel", "Manual", "FWD", "5-Seater", "1.5L CRDi", 1237000, "LED Projectors, Wireless Charger, Rear AC Vents"),
        (car_ids["hyundai-exter"], "SX Petrol MT", "Petrol", "Manual", "FWD", "5-Seater", "1.2L Kappa", 823000, "Electric Sunroof, Dashcam with Dual Camera, Projectors"),
        (car_ids["hyundai-exter"], "SX (O) Connect AMT", "Petrol", "AMT", "FWD", "5-Seater", "1.2L Kappa", 980000, "Smart AMT, BlueLink Telematics, Diamond Alloys"),
        (car_ids["hyundai-exter"], "SX Hy-CNG Duo", "CNG", "Manual", "FWD", "5-Seater", "1.2L Bi-Fuel CNG", 916000, "Dual Cylinder CNG Technology, Integrated Fire Extinguisher"),
        (car_ids["hyundai-verna"], "SX (O) Turbo DCT", "Petrol", "DCT", "FWD", "5-Seater", "1.5L Turbo GDi", 1742000, "Level 2 ADAS, Heated & Ventilated Seats, Switchable Climate Controls"),

        # Kia
        (car_ids["kia-seltos"], "HTK Plus Petrol iMT", "Petrol", "iMT", "FWD", "5-Seater", "1.5L Smartstream", 1350000, "Clutchless Manual, Panoramic Sunroof, LED DRLs"),
        (car_ids["kia-seltos"], "HTX Petrol IVT", "Petrol", "IVT", "FWD", "5-Seater", "1.5L Smartstream", 1660000, "Dual Zone Climate, Ambient Lighting, 17-inch Alloys"),
        (car_ids["kia-seltos"], "HTX Plus Diesel AT", "Diesel", "Automatic", "FWD", "5-Seater", "1.5L CRDi VGT", 1870000, "Bose 8-Speaker Sound, Ventilated Seats, 8-Way Powered Seat"),
        (car_ids["kia-seltos"], "GTX Plus Turbo DCT", "Petrol", "DCT", "FWD", "5-Seater", "1.5L Turbo GDi", 2000000, "Level 2 ADAS (17 Features), 360 View, Electronic Parking Brake"),
        (car_ids["kia-sonet"], "HTX Diesel AT", "Diesel", "Automatic", "FWD", "5-Seater", "1.5L CRDi", 1310000, "Sunroof, LED Headlamps, Drive & Traction Modes"),
        (car_ids["kia-sonet"], "HTX Turbo iMT", "Petrol", "iMT", "FWD", "5-Seater", "1.0L Turbo GDi", 1150000, "Paddle Shifters, Smart Key, Cruise Control"),
        (car_ids["kia-carens"], "Prestige Plus Diesel MT", "Diesel", "Manual", "FWD", "7-Seater", "1.5L CRDi", 1520000, "Auto AC, 16-inch Alloys, Keyless Entry, One-Touch Tumble"),
        (car_ids["kia-carens"], "Luxury Plus Diesel AT", "Diesel", "Automatic", "FWD", "6-Seater", "1.5L CRDi", 1920000, "Ventilated Seats, Bose Audio, Sky Light Ambient Roof"),

        # Toyota
        (car_ids["toyota-urban-cruiser-hyryder"], "S CNG MT", "CNG", "Manual", "FWD", "5-Seater", "1.5L K15C CNG", 1371000, "Factory Fitted CNG, 26.6 km/kg Mileage, 7-inch Touchscreen"),
        (car_ids["toyota-urban-cruiser-hyryder"], "G NeoDrive AT", "Petrol", "Automatic", "FWD", "5-Seater", "1.5L K-Series", 1579000, "6-Speed AT, 9-inch Smart Playcast, Panoramic Roof"),
        (car_ids["toyota-urban-cruiser-hyryder"], "V Strong Hybrid e-CVT", "Hybrid", "e-CVT", "FWD", "5-Seater", "1.5L TNGA Atkinson Cycle Hybrid", 1999000, "Pure EV Drive Mode, 27.97 km/l Mileage, Ventilated Seats"),
        (car_ids["toyota-innova-hycross"], "GX 8-Str Petrol AT", "Petrol", "Automatic", "FWD", "8-Seater", "2.0L TNGA Petrol", 1977000, "Spacious 8-Seater, Apple CarPlay, Push Button Start"),
        (car_ids["toyota-innova-hycross"], "ZX (O) Strong Hybrid e-CVT", "Hybrid", "e-CVT", "FWD", "7-Seater", "2.0L TNGA 5th Gen Hybrid", 3098000, "Ottoman Powered Captain Seats, Panoramic Roof, ADAS Suite"),
        (car_ids["toyota-fortuner"], "4x2 Petrol MT", "Petrol", "Manual", "RWD", "7-Seater", "2.7L Dual VVT-i", 3343000, "Touchscreen, Leather Seats, Cruise Control"),
        (car_ids["toyota-fortuner"], "4x4 Diesel AT", "Diesel", "Automatic", "4x4", "7-Seater", "2.8L Turbo Diesel", 4232000, "500 Nm Torque, Auto Limited Slip Differential, JBL Audio"),
        (car_ids["toyota-glanza"], "G AMT", "Petrol", "AMT", "FWD", "5-Seater", "1.2L K-Series DualJet", 920000, "Smart AMT, LED Projectors, Smartplay Cast, 6 Airbags"),
        (car_ids["toyota-glanza"], "S CNG MT", "CNG", "Manual", "FWD", "5-Seater", "1.2L Bi-Fuel CNG", 865000, "30.61 km/kg Mileage, Touchscreen Audio, Tilt Steering"),

        # Maruti Suzuki
        (car_ids["maruti-suzuki-brezza"], "VXi CNG MT", "CNG", "Manual", "FWD", "5-Seater", "1.5L K15C CNG", 1065000, "Factory Fitted Dual Interdependent ECU CNG, 25.5 km/kg"),
        (car_ids["maruti-suzuki-brezza"], "ZXi AT", "Petrol", "Automatic", "FWD", "5-Seater", "1.5L K15C Smart Hybrid", 1255000, "Paddle Shifters, Electric Sunroof, Cruise Control"),
        (car_ids["maruti-suzuki-brezza"], "ZXi Plus AT", "Petrol", "Automatic", "FWD", "5-Seater", "1.5L K15C", 1398000, "360 View Camera, Head-Up Display, Sunroof, Arkamys Audio"),
        (car_ids["maruti-suzuki-grand-vitara"], "Delta CNG MT", "CNG", "Manual", "FWD", "5-Seater", "1.5L K15C CNG", 1315000, "Suzuki Connect, SmartPlay Pro, ESP, Hill Hold"),
        (car_ids["maruti-suzuki-grand-vitara"], "Zeta AT", "Petrol", "Automatic", "FWD", "5-Seater", "1.5L K15C Smart Hybrid", 1541000, "6 Airbags, LED Headlamps, 9-inch SmartPlay Pro+"),
        (car_ids["maruti-suzuki-grand-vitara"], "Alpha Strong Hybrid e-CVT", "Hybrid", "e-CVT", "FWD", "5-Seater", "1.5L Intelligent Electric Hybrid", 1999000, "Panoramic Sunroof, Ventilated Seats, 360 Camera, 27.97 km/l"),
        (car_ids["maruti-suzuki-swift"], "ZXi Plus MT", "Petrol", "Manual", "FWD", "5-Seater", "1.2L Z-Series 3-Cyl", 900000, "9-inch Touchscreen, LED DRLs, Wireless Charger, 6 Airbags"),
        (car_ids["maruti-suzuki-swift"], "VXi AMT", "Petrol", "AMT", "FWD", "5-Seater", "1.2L Z-Series", 780000, "Smooth AGS Automatic, ESP, Hill Hold, Remote Keyless"),
        (car_ids["maruti-suzuki-swift"], "VXi CNG MT", "CNG", "Manual", "FWD", "5-Seater", "1.2L Z-Series CNG", 820000, "32.85 km/kg Mileage, Dual Airbags, ABS with EBD"),
        (car_ids["maruti-suzuki-baleno"], "Alpha AMT", "Petrol", "AMT", "FWD", "5-Seater", "1.2L DualJet Dual VVT", 988000, "Head Up Display, 360 Camera, 9-inch SmartPlay Pro+"),
        (car_ids["maruti-suzuki-baleno"], "Zeta CNG MT", "CNG", "Manual", "FWD", "5-Seater", "1.2L CNG", 928000, "6 Airbags, LED Projector Headlamps, Rear Camera"),
        (car_ids["maruti-suzuki-fronx"], "Alpha Turbo AT", "Petrol", "Automatic", "FWD", "5-Seater", "1.0L Boosterjet Turbo", 1298000, "6-Speed AT with Paddle Shifters, HUD, 360 Camera"),
        (car_ids["maruti-suzuki-fronx"], "Delta Plus AMT", "Petrol", "AMT", "FWD", "5-Seater", "1.2L DualJet", 878000, "AGS Transmission, Auto LED Headlamps, Touchscreen"),
        (car_ids["maruti-suzuki-dzire"], "ZXi Plus AMT", "Petrol", "AMT", "FWD", "5-Seater", "1.2L Z-Series", 1014000, "Electric Sunroof, 360 HD Camera, 6 Airbags Standard"),
        (car_ids["maruti-suzuki-dzire"], "VXi CNG MT", "CNG", "Manual", "FWD", "5-Seater", "1.2L Z-Series CNG", 874000, "33.73 km/kg Mileage, ESP, Rear AC Vents")
    ]

    for v in variants_data:
        cursor.execute("""
        INSERT INTO variants (car_id, name, fuel_type, transmission, drivetrain, seating, engine_spec, ex_showroom_price, key_features)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, v)

    # Re-fetch variant map by (car_id, name)
    cursor.execute("SELECT id, car_id, name FROM variants;")
    v_rows = cursor.fetchall()
    v_map = {}
    for r in v_rows:
        v_map[(r["car_id"], r["name"])] = r["id"]

    # 4. Insert Inventory for all variants across Dealerships
    # Note: All inventory is IN_STOCK with units_available >= 1 (strictly available cars only)
    inventory_data = [
        # TATA MOTORS - Haldwani (Gola Ganapati Motors)
        (dealer_ids["gola-ganapati-tata-haldwani"], v_map[(car_ids["tata-nexon"], "Creative Plus DCA")], "IN_STOCK", 3, 0, "Calgary White, Daytona Grey, Flame Red", 1, "Ready showroom units."),
        (dealer_ids["gola-ganapati-tata-haldwani"], v_map[(car_ids["tata-nexon"], "Creative iCNG")], "IN_STOCK", 2, 0, "Pristine White, Pure Grey", 1, "Immediate delivery."),
        (dealer_ids["gola-ganapati-tata-haldwani"], v_map[(car_ids["tata-nexon"], "Empowered Plus LR EV")], "IN_STOCK", 2, 0, "Empowered Oxide, Pristine White", 1, "Ready electric inventory."),
        (dealer_ids["gola-ganapati-tata-haldwani"], v_map[(car_ids["tata-punch"], "Accomplished Dazzle MT")], "IN_STOCK", 4, 0, "Atomic Orange, Foliage Green, Daytona Grey", 1, "Immediate delivery."),
        (dealer_ids["gola-ganapati-tata-haldwani"], v_map[(car_ids["tata-curvv"], "Creative S Petrol DCA")], "IN_STOCK", 2, 0, "Cosmic Gold, Pristine White", 1, "Ready units available."),
        (dealer_ids["gola-ganapati-tata-haldwani"], v_map[(car_ids["tata-harrier"], "Adventure Plus A AT")], "IN_STOCK", 2, 0, "Sunlit Yellow, Ash Grey", 1, "Showroom floor unit."),

        # TATA MOTORS - Rudrapur (Amit Auto)
        (dealer_ids["amit-auto-tata-rudrapur"], v_map[(car_ids["tata-nexon"], "Fearless Plus S Diesel AT")], "IN_STOCK", 3, 0, "Fearless Purple, Daytona Grey", 1, "Ready showroom units."),
        (dealer_ids["amit-auto-tata-rudrapur"], v_map[(car_ids["tata-punch"], "Adventure iCNG")], "IN_STOCK", 3, 0, "Tropical Mist, White Roof", 1, "Ready delivery."),
        (dealer_ids["amit-auto-tata-rudrapur"], v_map[(car_ids["tata-punch"], "Accomplished AMT")], "IN_STOCK", 2, 0, "Daytona Grey, Orcus White", 1, "Immediate allotment."),
        (dealer_ids["amit-auto-tata-rudrapur"], v_map[(car_ids["tata-curvv"], "Accomplished Plus A Diesel AT")], "IN_STOCK", 2, 0, "Pristine White, Flame Red", 1, "Ready stock in showroom."),
        (dealer_ids["amit-auto-tata-rudrapur"], v_map[(car_ids["tata-safari"], "Accomplished Plus 6-Str AT")], "IN_STOCK", 1, 0, "Starlight, Oberon Black", 1, "Top spec 6-seater ready."),

        # MAHINDRA - Haldwani (Bajrang Motors)
        (dealer_ids["bajrang-motors-mahindra-haldwani"], v_map[(car_ids["mahindra-thar-roxx"], "AX7 L 4x4 Diesel AT")], "IN_STOCK", 3, 0, "Stealth Black, Everest White", 1, "Ready floor units."),
        (dealer_ids["bajrang-motors-mahindra-haldwani"], v_map[(car_ids["mahindra-thar-roxx"], "MX3 Petrol MT")], "IN_STOCK", 2, 0, "Deep Forest, Stealth Black", 1, "Immediate delivery."),
        (dealer_ids["bajrang-motors-mahindra-haldwani"], v_map[(car_ids["mahindra-scorpio-n"], "Z8 L Diesel AT 4x4")], "IN_STOCK", 2, 0, "Napoli Black, Everest White", 1, "Ready delivery."),
        (dealer_ids["bajrang-motors-mahindra-haldwani"], v_map[(car_ids["mahindra-scorpio-n"], "Z8 Petrol AT")], "IN_STOCK", 2, 0, "Dazzling Silver, Deep Forest", 1, "Ready stock."),
        (dealer_ids["bajrang-motors-mahindra-haldwani"], v_map[(car_ids["mahindra-xuv700"], "AX7 L 7-Str Petrol AT")], "IN_STOCK", 2, 0, "Midnight Black, Everest White", 1, "Ready luxury stock."),
        (dealer_ids["bajrang-motors-mahindra-haldwani"], v_map[(car_ids["mahindra-xuv-3xo"], "AX5 Petrol AT")], "IN_STOCK", 3, 0, "Tango Red, Stealth Black", 1, "Immediate delivery."),
        (dealer_ids["bajrang-motors-mahindra-haldwani"], v_map[(car_ids["mahindra-thar"], "LX 4x4 Hard Top Diesel MT")], "IN_STOCK", 2, 0, "Red Rage, Napoli Black", 1, "Off-road demo unit and fresh stock."),

        # MAHINDRA - Rudrapur (Kumar Autowheels)
        (dealer_ids["kumar-autowheels-mahindra-rudrapur"], v_map[(car_ids["mahindra-thar-roxx"], "AX5 L Diesel AT")], "IN_STOCK", 2, 0, "Battleship Grey, Stealth Black", 1, "Ready stock."),
        (dealer_ids["kumar-autowheels-mahindra-rudrapur"], v_map[(car_ids["mahindra-scorpio-n"], "Z4 Diesel MT")], "IN_STOCK", 3, 0, "Dazzling Silver, Napoli Black", 1, "Ready units."),
        (dealer_ids["kumar-autowheels-mahindra-rudrapur"], v_map[(car_ids["mahindra-xuv700"], "AX7 Diesel AT AWD")], "IN_STOCK", 1, 0, "Electric Blue, Everest White", 1, "AWD unit ready."),
        (dealer_ids["kumar-autowheels-mahindra-rudrapur"], v_map[(car_ids["mahindra-xuv-3xo"], "AX7 L Diesel MT")], "IN_STOCK", 2, 0, "Citrine Yellow, Stealth Black", 1, "Ready units."),
        (dealer_ids["kumar-autowheels-mahindra-rudrapur"], v_map[(car_ids["mahindra-thar"], "LX 4x4 Hard Top Petrol AT")], "IN_STOCK", 1, 0, "Deep Grey, Red Rage", 1, "Immediate allocation."),
        (dealer_ids["kumar-autowheels-mahindra-rudrapur"], v_map[(car_ids["mahindra-bolero"], "B6 (O) Diesel MT")], "IN_STOCK", 4, 0, "Diamond White, Silver", 1, "Commercial and private stock."),

        # HYUNDAI - Haldwani (Sachin Hyundai)
        (dealer_ids["sachin-hyundai-haldwani"], v_map[(car_ids["hyundai-creta"], "SX (O) Turbo Petrol DCT")], "IN_STOCK", 3, 0, "Abyss Black, Ranger Khaki", 1, "Top model ready."),
        (dealer_ids["sachin-hyundai-haldwani"], v_map[(car_ids["hyundai-creta"], "S (O) Petrol IVT")], "IN_STOCK", 2, 0, "Atlas White, Titan Grey", 1, "Ready stock."),
        (dealer_ids["sachin-hyundai-haldwani"], v_map[(car_ids["hyundai-venue"], "SX (O) Turbo DCT")], "IN_STOCK", 3, 0, "Titan Grey, Abyss Black", 1, "Ready delivery."),
        (dealer_ids["sachin-hyundai-haldwani"], v_map[(car_ids["hyundai-exter"], "SX Petrol MT")], "IN_STOCK", 3, 0, "Ranger Khaki, Atlas White", 1, "Ready stock."),
        (dealer_ids["sachin-hyundai-haldwani"], v_map[(car_ids["hyundai-verna"], "SX (O) Turbo DCT")], "IN_STOCK", 2, 0, "Starry Night, Abyss Black", 1, "Ready sedan unit."),

        # HYUNDAI - Rudrapur (Bindal Hyundai)
        (dealer_ids["bindal-hyundai-rudrapur"], v_map[(car_ids["hyundai-creta"], "SX (O) Diesel AT")], "IN_STOCK", 2, 0, "Robust Emerald Pearl, Atlas White", 1, "Ready stock on showroom floor."),
        (dealer_ids["bindal-hyundai-rudrapur"], v_map[(car_ids["hyundai-creta"], "EX Diesel MT")], "IN_STOCK", 3, 0, "Titan Grey, Abyss Black", 1, "Ready delivery."),
        (dealer_ids["bindal-hyundai-rudrapur"], v_map[(car_ids["hyundai-venue"], "S (O) Plus CNG")], "IN_STOCK", 2, 0, "Atlas White, Fiery Red", 1, "Factory CNG ready."),
        (dealer_ids["bindal-hyundai-rudrapur"], v_map[(car_ids["hyundai-exter"], "SX Hy-CNG Duo")], "IN_STOCK", 3, 0, "Cosmic Blue, Atlas White", 1, "Dual cylinder CNG in stock."),
        (dealer_ids["bindal-hyundai-rudrapur"], v_map[(car_ids["hyundai-exter"], "SX (O) Connect AMT")], "IN_STOCK", 2, 0, "Ranger Khaki, Starry Night", 1, "Automatic ready."),

        # KIA - Haldwani (Classic Kia)
        (dealer_ids["classic-kia-haldwani"], v_map[(car_ids["kia-seltos"], "HTX Plus Diesel AT")], "IN_STOCK", 2, 0, "Pewter Olive, Glacier White Pearl", 1, "Immediate delivery."),
        (dealer_ids["classic-kia-haldwani"], v_map[(car_ids["kia-seltos"], "GTX Plus Turbo DCT")], "IN_STOCK", 2, 0, "Aurora Black Pearl, Intense Red", 1, "GTX turbo ready."),
        (dealer_ids["classic-kia-haldwani"], v_map[(car_ids["kia-sonet"], "HTX Diesel AT")], "IN_STOCK", 3, 0, "Aurora Black Pearl, Gravity Grey", 1, "Ready test drive and delivery."),
        (dealer_ids["classic-kia-haldwani"], v_map[(car_ids["kia-carens"], "Luxury Plus Diesel AT")], "IN_STOCK", 2, 0, "Imperial Blue, Glacier White Pearl", 1, "6-seater ready."),

        # KIA - Rudrapur (Classic Kia)
        (dealer_ids["classic-kia-rudrapur"], v_map[(car_ids["kia-seltos"], "HTK Plus Petrol iMT")], "IN_STOCK", 3, 0, "Gravity Grey, Sparkling Silver", 1, "Ready units."),
        (dealer_ids["classic-kia-rudrapur"], v_map[(car_ids["kia-seltos"], "HTX Petrol IVT")], "IN_STOCK", 2, 0, "Glacier White Pearl, Pewter Olive", 1, "Automatic ready."),
        (dealer_ids["classic-kia-rudrapur"], v_map[(car_ids["kia-sonet"], "HTX Turbo iMT")], "IN_STOCK", 2, 0, "Intense Red, Aurora Black Pearl", 1, "Ready stock."),
        (dealer_ids["classic-kia-rudrapur"], v_map[(car_ids["kia-carens"], "Prestige Plus Diesel MT")], "IN_STOCK", 2, 0, "Imperial Blue, Clear White", 1, "7-seater ready."),

        # TOYOTA - Haldwani (Trust Toyota)
        (dealer_ids["trust-toyota-haldwani"], v_map[(car_ids["toyota-urban-cruiser-hyryder"], "V Strong Hybrid e-CVT")], "IN_STOCK", 3, 0, "Cafe White, Gaming Grey", 1, "High efficiency hybrid ready."),
        (dealer_ids["trust-toyota-haldwani"], v_map[(car_ids["toyota-urban-cruiser-hyryder"], "G NeoDrive AT")], "IN_STOCK", 2, 0, "Sporting Red, Enticing Silver", 1, "Automatic ready."),
        (dealer_ids["trust-toyota-haldwani"], v_map[(car_ids["toyota-fortuner"], "4x4 Diesel AT")], "IN_STOCK", 2, 0, "Attitude Black, Platinum White Pearl", 1, "Ready Fortuner unit."),
        (dealer_ids["trust-toyota-haldwani"], v_map[(car_ids["toyota-glanza"], "G AMT")], "IN_STOCK", 3, 0, "Sporting Red, Cafe White", 1, "Ready stock."),

        # TOYOTA - Rudrapur (Trust Toyota)
        (dealer_ids["trust-toyota-rudrapur"], v_map[(car_ids["toyota-innova-hycross"], "ZX (O) Strong Hybrid e-CVT")], "IN_STOCK", 2, 0, "Blackish Ageha Glass Flake, Platinum White Pearl", 1, "Showroom floor unit."),
        (dealer_ids["trust-toyota-rudrapur"], v_map[(car_ids["toyota-innova-hycross"], "GX 8-Str Petrol AT")], "IN_STOCK", 2, 0, "Super White, Silver Metallic", 1, "Ready 8-seater."),
        (dealer_ids["trust-toyota-rudrapur"], v_map[(car_ids["toyota-urban-cruiser-hyryder"], "S CNG MT")], "IN_STOCK", 3, 0, "Super White, Enticing Silver", 1, "Factory CNG ready."),
        (dealer_ids["trust-toyota-rudrapur"], v_map[(car_ids["toyota-glanza"], "S CNG MT")], "IN_STOCK", 2, 0, "Insta Blue, Cafe White", 1, "CNG hatchback ready."),

        # MARUTI SUZUKI - Haldwani (Nanital Moters)
        (dealer_ids["nanital-moters-maruti-haldwani"], v_map[(car_ids["maruti-suzuki-brezza"], "ZXi Plus AT")], "IN_STOCK", 4, 0, "Magma Grey, Pearl Arctic White", 1, "Top variant ready."),
        (dealer_ids["nanital-moters-maruti-haldwani"], v_map[(car_ids["maruti-suzuki-brezza"], "VXi CNG MT")], "IN_STOCK", 3, 0, "Sizzling Red, Splendid Silver", 1, "Brezza CNG ready."),
        (dealer_ids["nanital-moters-maruti-haldwani"], v_map[(car_ids["maruti-suzuki-grand-vitara"], "Alpha Strong Hybrid e-CVT")], "IN_STOCK", 3, 0, "Nexa Blue, Grandeur Grey", 1, "Strong Hybrid ready."),
        (dealer_ids["nanital-moters-maruti-haldwani"], v_map[(car_ids["maruti-suzuki-swift"], "ZXi Plus MT")], "IN_STOCK", 5, 0, "Luster Blue, Sizzling Red, Magma Grey", 1, "New Swift top variant ready."),
        (dealer_ids["nanital-moters-maruti-haldwani"], v_map[(car_ids["maruti-suzuki-swift"], "VXi CNG MT")], "IN_STOCK", 3, 0, "Pearl Arctic White, Splendid Silver", 1, "Swift CNG ready."),
        (dealer_ids["nanital-moters-maruti-haldwani"], v_map[(car_ids["maruti-suzuki-baleno"], "Alpha AMT")], "IN_STOCK", 3, 0, "Nexa Blue, Pearl Arctic White", 1, "Ready stock."),

        # MARUTI SUZUKI - Rudrapur (Akansha Automobiles)
        (dealer_ids["akansha-automobiles-maruti-rudrapur"], v_map[(car_ids["maruti-suzuki-brezza"], "ZXi AT")], "IN_STOCK", 3, 0, "Brave Khaki, Splendid Silver", 1, "Ready stock on Kashipur Road."),
        (dealer_ids["akansha-automobiles-maruti-rudrapur"], v_map[(car_ids["maruti-suzuki-grand-vitara"], "Delta CNG MT")], "IN_STOCK", 3, 0, "Grandeur Grey, Pearl Arctic White", 1, "Grand Vitara CNG ready."),
        (dealer_ids["akansha-automobiles-maruti-rudrapur"], v_map[(car_ids["maruti-suzuki-grand-vitara"], "Zeta AT")], "IN_STOCK", 2, 0, "Splendid Silver, Nexa Blue", 1, "Ready stock."),
        (dealer_ids["akansha-automobiles-maruti-rudrapur"], v_map[(car_ids["maruti-suzuki-swift"], "VXi AMT")], "IN_STOCK", 4, 0, "Novel Orange, Magma Grey", 1, "Automatic Swift ready."),
        (dealer_ids["akansha-automobiles-maruti-rudrapur"], v_map[(car_ids["maruti-suzuki-fronx"], "Alpha Turbo AT")], "IN_STOCK", 2, 0, "Bluish Black, Earthen Brown", 1, "Turbo Fronx available."),
        (dealer_ids["akansha-automobiles-maruti-rudrapur"], v_map[(car_ids["maruti-suzuki-fronx"], "Delta Plus AMT")], "IN_STOCK", 3, 0, "Grandeur Grey, Splendid Silver", 1, "Ready delivery."),
        (dealer_ids["akansha-automobiles-maruti-rudrapur"], v_map[(car_ids["maruti-suzuki-dzire"], "ZXi Plus AMT")], "IN_STOCK", 3, 0, "Alluring Blue, Gallant Red", 1, "Sunroof Dzire ready."),
        (dealer_ids["akansha-automobiles-maruti-rudrapur"], v_map[(car_ids["maruti-suzuki-dzire"], "VXi CNG MT")], "IN_STOCK", 4, 0, "Pearl Arctic White, Magma Grey", 1, "New Dzire CNG in stock.")
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
