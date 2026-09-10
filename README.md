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

1. **Multi-Attribute Showroom Stock Explorer**:
   - Filter dynamically across **Brand**, **Model**, **Variant**, **Fuel Type** (Petrol, Diesel, CNG, Electric, Hybrid), **Transmission** (Manual, Automatic, AMT, DCT/DCA, Torque Converter, e-CVT), and **Exterior Color**.
   - Dedicated **Submit** and **Clear All** controls for streamlined filtering.
   - Comprehensive model database covering all genuine OEM variants, trims, and official exterior color options.

2. **Dynamic Live Feeds**:
   - **Randomized Discovery**: Vehicle cards are randomized upon every page refresh to ensure fair, diverse vehicle visibility across all manufacturers.
   - **Live Stock Indicator**: Cards display dynamic morning live verification timestamps (*e.g., "Stock live at 10:45 AM"*).

3. **Privacy-First Customer Experience**:
   - **No Hidden Markups**: *"Don't pay extra/premium for the car you are looking for."*
   - **Confidential Dealer Relations**: Specific dealership branch names and internal locations are kept confidential on customer-facing cards to protect showroom partner networks while verifying authentic live inventory.
   - **Flexible Location Input**: Customers can specify any delivery location without rigid dropdowns or RTO restrictions.

4. **1-Click Dealership Connect & Lead Management**:
   - **Direct WhatsApp Chat**: Generates pre-formatted WhatsApp inquiries specifying exact vehicle model, variant, transmission, fuel, and color.
   - **Test Drive Scheduling**: Book showroom or doorstep test drive sessions.
   - **Instant Callback**: Submit customer contact details (Name & Mobile required; Email and Location optional).

5. **Showroom Staff & Dealer Management Portal (`/dealer` & `/admin/login`)**:
   - Showroom sales executives and inventory managers can update stock counts, toggle status (`Ready`, `In Transit`, `Allocated`), and adjust estimated waiting periods.
   - Customer inquiry pipeline with status tracking (`New`, `Contacted`, `Test Drive Scheduled`, `Delivered`).
   - Quick WhatsApp response trigger directly from the dealer leads desk.

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
- **Showroom Staff & Admin Login**: [http://127.0.0.1:8000/admin/login](http://127.0.0.1:8000/admin/login)
- **Dealer Management Portal**: [http://127.0.0.1:8000/dealer](http://127.0.0.1:8000/dealer)
- **Interactive API Documentation (Swagger)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
