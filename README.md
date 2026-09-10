<p align="center">
  <img src="app/static/images/logo_transparent.png" alt="ScoutMyVehicle - Find | Verify | Drive" width="380">
</p>

# ScoutMyVehicle 🚗
### Real-Time Multi-Brand Showroom Stock & Allocation Tracker
**FIND | VERIFY | DRIVE**

**ScoutMyVehicle** connects car buyers with authorized dealership networks across **9 major automotive brands**. It eliminates long dealership waiting periods by surfacing real-time showroom ready stock, in-transit units, and verified allocations—empowering buyers to secure the vehicle they want without paying extra dealer markups or premiums.

---

## 🏢 Authorized Brand Network

ScoutMyVehicle covers **87+ models** and **670+ active variants** across 18 authorized dealership nodes representing leading OEMs:

| Brand | Emblem / Network | Popular Showroom Models |
| :--- | :--- | :--- |
| **Maruti Suzuki Arena** | Arena Network | Swift, Brezza, Dzire, Ertiga, WagonR, Alto K10 |
| **Maruti Suzuki Nexa** | Nexa Network | Grand Vitara, Fronx, Baleno, Jimny, XL6, Invicto |
| **Tata Motors** | Tata Motors Passenger Vehicles | Nexon, Punch, Harrier, Safari, Curvv, Altroz, Tiago |
| **Mahindra** | Mahindra & Mahindra | Thar Roxx, Scorpio-N, XUV700, XUV 3XO, Thar, Scorpio Classic |
| **Hyundai** | Hyundai Motor India | Creta, Venue, Exter, i20, Alcazar, Verna, Tucson |
| **Kia** | Kia India | Seltos, Sonet, Carens, Carnival, EV6 |
| **Toyota** | Toyota Kirloskar Motor | Innova Hycross, Urban Cruiser Hyryder, Fortuner, Glanza, Hilux |
| **Volkswagen** | Volkswagen India | Virtus, Taigun, Tiguan |
| **Škoda** | Škoda Auto India | Slavia, Kushaq, Kodiaq, Kylaq |
| **Nissan** | Nissan Motor India | Magnite, X-Trail |

---

## 🚀 Key Features

1. **Modern Header & Responsive Navigation**:
   - **Centered Identity**: Prominently centered `ScoutMyVehicle` brand and matching `FIND | VERIFY | DRIVE` tagline with crimson red accents and matching typography.
   - **Top-Right Hamburger Menu**: Compact dropdown navigation housing **Brands**, **Banks & Finance**, and **How it works** for an uncluttered browsing experience.
   - **Top-Left Emblem Logo**: Clean vector automotive crest keeping brand identity intact.

2. **Model-Centric Catalog with In-Card Configuration Selectors**:
   - Streamlined browsing by distinct car models (reducing catalog clutter from hundreds of duplicate variant cards).
   - Interactive selectors directly inside each model card for **Car Variant**, **Fuel Type**, **Transmission**, and **Exterior Colour**.
   - Dynamic real-time updates of vehicle specifications, ex-showroom pricing, and stock status right inside the card.
   - Clean top-level filter controls for **Brand** and **Model** with dedicated **Submit** and **Clear all** buttons.

3. **Authorized Bank & Auto Finance Partners**:
   - Dedicated financing modal featuring premier institutional automotive lending partners with verified official car loan interest rates:
     - **State Bank of India (SBI)**: `starting from 8.85%` (SBI Car Loan & YONO Auto Financing).
     - **Punjab National Bank (PNB)**: `starting from 8.75%` (PNB Pride & Saarthak Schemes).
     - **HDFC Bank**: `starting from 8.75%` (Fast-track 30-min sanction, 100% on-road funding).
     - **Chola Mandalam (Murugappa Group)**: `starting from 9.50%` (Premier vehicle NBFC for self-employed/rural buyers).
   - **Interactive Live Car Loan EMI Calculator**: Real-time slider-based monthly EMI estimates, total interest, and total payable calculations.
   - Preferred bank partner selection seamlessly attached to customer inquiries.

4. **1-Click WhatsApp Dispatch & Google Sheets Lead Recording**:
   - **WhatsApp Instant Dispatch**: Upon inquiry submission, full vehicle configuration and customer details are automatically formatted and forwarded to WhatsApp number **`+919275251003`**.
   - **Google Sheets Integration**: Every submitted customer inquiry is automatically logged to Google Sheet format (`data/inquiries_google_sheet.csv`), available via live export (`/api/inquiries/export.csv`) or direct Google Apps Script Web App webhook.

5. **Dynamic Live Feeds & Privacy-First Buying**:
   - **Randomized Discovery**: Vehicle cards are randomized upon every page refresh to ensure fair, diverse vehicle visibility across all manufacturers.
   - **Live Stock Indicator**: Cards display dynamic morning live verification timestamps (*e.g., "Stock live at 10:45 AM"*).
   - **No Hidden Markups**: *"Don't pay extra/premium for the car you are looking for."*
   - **Confidential Dealer Relations**: Specific dealership branch names and internal locations are kept confidential on customer-facing cards to protect showroom partner networks while verifying authentic live inventory.

---

## 💻 Tech Stack

- **Backend**: Python 3.12, FastAPI, SQLite (`scoutmycar.db`), Pydantic models.
- **Frontend**: Tailwind CSS, Alpine.js, Lucide Icons, clean vector brand emblems.
- **Testing**: Python `unittest` test suite with automated database seeding and teardown isolation.

---

## 🛠️ Quick Start

### 1. Activate Virtual Environment
```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. Seed the Database
Seed all 18 dealerships, 87 car models, and 671 variants:
```powershell
python -m app.seed_data
```

### 3. Run the Application
```powershell
python run.py
```

### 4. Run the Test Suite
```powershell
python -m unittest tests/test_app.py
```

---

## 🌐 Application Endpoints

- **Customer Portal**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Inquiries Google Sheets Export**: [http://127.0.0.1:8000/api/inquiries/export.csv](http://127.0.0.1:8000/api/inquiries/export.csv)
- **Interactive API Documentation (Swagger)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
