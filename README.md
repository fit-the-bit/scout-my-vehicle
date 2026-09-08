# ScoutMyCar 🚙
### Live Mahindra Showroom Stock & Availability Tracker (Uttarakhand Edition)

ScoutMyCar connects prospective car buyers in Uttarakhand with authorized **Mahindra dealerships across Haldwani (UK-04) and Rudrapur (UK-06)**. It eliminates long waiting periods by surfacing real-time showroom ready stock, in-transit units, and cancelled booking allocations.

---

## 🏔️ Target Region & Dealerships

- **Haldwani (UK-04 - Nainital District)**:
  - **Dee Kay Motors - Mahindra Haldwani**: Bareilly - Nainital National Highway (Near Kathgodam)
  - **Nainital Motors - Mahindra Haldwani**: Rampur Road, Opposite Transport Nagar Gate No 2
- **Rudrapur (UK-06 - Udham Singh Nagar District)**:
  - **Dee Kay Motors - Mahindra Rudrapur**: Delhi - Nainital Highway (NH-109), Near Metropolis Mall
  - **Ananya Mahindra - Rudrapur**: Kashipur Bypass Road, Near Big Bazaar Chowk

---

## 🚀 Key Features

1. **Live Showroom Stock Explorer**:
   - Filter by City (**Haldwani** vs **Rudrapur** vs **All Uttarakhand**).
   - Filter by Mahindra Model (**Thar Roxx**, **Scorpio-N**, **XUV700**, **XUV 3XO**, **Thar 3-Door**, **Scorpio Classic**, **Bolero Neo**).
   - Filter by availability: 🟢 **Ready in Showroom (Immediate Delivery)**, 🟡 **In Transit (3-7 Days)**, 🟠 **Waitlist / Regular Booking**.

2. **Cross-City Showroom Comparison**:
   - Compare stock, available colors, and waiting periods side-by-side between Haldwani and Rudrapur dealers for any car model.

3. **1-Click Dealership Connect**:
   - **Direct WhatsApp Chat**: Generates a pre-filled WhatsApp message specifying the exact car model, trim, color, and showroom branch.
   - **Instant Callback & Hold Unit Request**: Direct notification sent to the showroom sales desk.
   - **Test Drive Scheduler**: Book showroom or doorstep test drives across Haldwani, Rudrapur, Kathgodam, or Pantnagar.

4. **Uttarakhand On-Road Price Calculator**:
   - Transparent price breakdown including Ex-showroom, Uttarakhand State RTO Road Tax (UK-04 vs UK-06), Comprehensive Insurance, FASTag, and TCS.

5. **Dealership Management Portal (`/dealer`)**:
   - Showroom sales managers can update vehicle status (`Ready`, `Transit`, `Waitlist`), adjust stock units, update waiting weeks, and toggle test-drive car availability.
   - Live Customer Leads inbox with instant WhatsApp follow-up and status updates (`New`, `Contacted`, `Test Drive Done`, `Closed`).

---

## 💻 Tech Stack

- **Backend**: FastAPI (Python 3.12), SQLite (`scoutmycar.db`), Pydantic models.
- **Frontend**: Tailwind CSS, Alpine.js, Lucide Icons, Modern Responsive Design.

---

## 🛠️ Quick Start

```powershell
# 1. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 2. Seed the database with Uttarakhand dealerships & Mahindra stock (done automatically on start)
python -m app.seed_data

# 3. Start the application
python run.py
```

Open your browser at:
- **Customer Portal**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Dealer Management Portal**: [http://127.0.0.1:8000/dealer](http://127.0.0.1:8000/dealer)
- **Interactive API Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
