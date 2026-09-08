import unittest
import sys
import os

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from app.main import app
from app.seed_data import seed

class TestScoutMyVehicle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Ensure fresh seed
        seed()
        cls.client = TestClient(app)

    def test_home_page_renders(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("ScoutMyVehicle", response.text)
        self.assertIn("The smarter way to find your car.", response.text)
        self.assertIn("Looking for a car? Let us find it.", response.text)
        self.assertIn("Others", response.text)
        self.assertIn("Customer's Location", response.text)
        self.assertIn("Car Variant", response.text)
        self.assertIn("blurred-dealer", response.text)
        # Verify direct WhatsApp/Call buttons removed from cards and replaced with inquiry CTA
        self.assertIn("Check Availability & Connect", response.text)
        self.assertIn("Purchase Timeline", response.text)
        self.assertIn("0-15 days", response.text)
        self.assertIn("Do you need a finance", response.text)

    def test_dealer_portal_redirects_when_unauthenticated(self):
        response = self.client.get("/dealer", follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login", response.headers.get("location", ""))

    def test_admin_login_workflow(self):
        # 1. Login page renders
        login_page = self.client.get("/admin/login")
        self.assertEqual(login_page.status_code, 200)
        self.assertIn("Admin & Staff Login", login_page.text)
        self.assertIn("ScoutMyVehicle", login_page.text)

        # 2. Invalid login returns 401
        bad_login = self.client.post("/api/admin/login", json={
            "username": "admin",
            "password": "wrongpassword"
        })
        self.assertEqual(bad_login.status_code, 401)

        # 3. Valid login succeeds
        good_login = self.client.post("/api/admin/login", json={
            "username": "admin",
            "password": "scoutmycar2026",
            "next_url": "/dealer"
        })
        self.assertEqual(good_login.status_code, 200)
        data = good_login.json()
        self.assertTrue(data["success"])
        self.assertIn("scout_admin_session", good_login.cookies)

        # 4. Authenticated request to /dealer renders portal
        portal_res = self.client.get("/dealer", cookies=good_login.cookies)
        self.assertEqual(portal_res.status_code, 200)
        self.assertIn("Dealership Stock Manager", portal_res.text)
        self.assertIn("System Administrator", portal_res.text)
        self.assertIn("Sign out", portal_res.text)

        # 5. Logout redirects to login and clears cookie
        logout_res = self.client.get("/admin/logout", cookies=good_login.cookies, follow_redirects=False)
        self.assertEqual(logout_res.status_code, 302)
        self.assertIn("/admin/login", logout_res.headers.get("location", ""))

    def test_api_dealerships(self):
        # All 12 dealerships across 6 brands
        res = self.client.get("/api/dealerships")
        self.assertEqual(res.status_code, 200)
        dealers = res.json()
        self.assertEqual(len(dealers), 12)

        # Haldwani only (6 dealers)
        res_haldwani = self.client.get("/api/dealerships?city=Haldwani")
        self.assertEqual(res_haldwani.status_code, 200)
        haldwani_dealers = res_haldwani.json()
        self.assertEqual(len(haldwani_dealers), 6)
        self.assertTrue(all(d["city"] == "Haldwani" for d in haldwani_dealers))

        # Rudrapur only (6 dealers)
        res_rudrapur = self.client.get("/api/dealerships?city=Rudrapur")
        self.assertEqual(res_rudrapur.status_code, 200)
        rudrapur_dealers = res_rudrapur.json()
        self.assertEqual(len(rudrapur_dealers), 6)
        self.assertTrue(all(d["city"] == "Rudrapur" for d in rudrapur_dealers))

        # Brand filter (Tata Motors)
        res_tata = self.client.get("/api/dealerships?brand=Tata Motors")
        self.assertEqual(res_tata.status_code, 200)
        tata_dealers = res_tata.json()
        self.assertEqual(len(tata_dealers), 2)
        dealer_names = [d["name"] for d in tata_dealers]
        self.assertIn("Gola Ganapati Motors", dealer_names)
        self.assertIn("Amit Auto", dealer_names)

        # Brand filter (Maruti Suzuki)
        res_maruti = self.client.get("/api/dealerships?brand=Maruti Suzuki")
        self.assertEqual(res_maruti.status_code, 200)
        maruti_dealers = res_maruti.json()
        self.assertEqual(len(maruti_dealers), 2)
        m_dealer_names = [d["name"] for d in maruti_dealers]
        self.assertIn("Nanital Moters", m_dealer_names)
        self.assertIn("Akansha Automobiles", m_dealer_names)

    def test_api_brands(self):
        res = self.client.get("/api/brands")
        self.assertEqual(res.status_code, 200)
        brands = res.json()
        self.assertIn("Tata Motors", brands)
        self.assertIn("Mahindra", brands)
        self.assertIn("Hyundai", brands)
        self.assertIn("Kia", brands)
        self.assertIn("Toyota", brands)
        self.assertIn("Maruti Suzuki", brands)

    def test_api_cars(self):
        res = self.client.get("/api/cars")
        self.assertEqual(res.status_code, 200)
        cars = res.json()
        self.assertGreaterEqual(len(cars), 15)
        
        # Test brand filtering on cars
        res_hyundai = self.client.get("/api/cars?brand=Hyundai")
        self.assertEqual(res_hyundai.status_code, 200)
        hyundai_cars = res_hyundai.json()
        self.assertTrue(all(c["make"] == "Hyundai" for c in hyundai_cars))

    def test_api_inventory_filtering(self):
        # Test city filter
        res_haldwani = self.client.get("/api/inventory?city=Haldwani")
        self.assertEqual(res_haldwani.status_code, 200)
        items = res_haldwani.json()
        self.assertGreater(len(items), 0)
        self.assertTrue(all(i["dealer_city"] == "Haldwani" for i in items))

        # Test brand filter
        res_kia = self.client.get("/api/inventory?brand=Kia")
        self.assertEqual(res_kia.status_code, 200)
        kia_items = res_kia.json()
        self.assertGreater(len(kia_items), 0)
        self.assertTrue(all("Kia" in i["car_brand"] or "Kia" in i["dealer_brand"] for i in kia_items))

        # Test Customer Location 'Others' returns inventory without restriction
        res_others = self.client.get("/api/inventory?customer_location=Others")
        self.assertEqual(res_others.status_code, 200)
        others_items = res_others.json()
        self.assertGreater(len(others_items), 10)

        # Test status filter
        res_stock = self.client.get("/api/inventory?status=IN_STOCK")
        self.assertEqual(res_stock.status_code, 200)
        stock_items = res_stock.json()
        self.assertTrue(all(i["status"] == "IN_STOCK" for i in stock_items))

    def test_api_compare(self):
        res = self.client.get("/api/compare/tata-nexon")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("tata-nexon", data["car"]["slug"])
        self.assertGreaterEqual(len(data["dealerships"]), 12)

    def test_inquiry_creation_and_dealer_view(self):
        # Create inquiry with purchase timeline and finance preference
        payload = {
            "dealership_id": 1,
            "car_id": 1,
            "variant_id": 1,
            "customer_name": "Rohan Rawat",
            "customer_phone": "+91 98970 11223",
            "customer_city": "Haldwani",
            "inquiry_type": "availability_check",
            "buying_timeline": "0-15 days",
            "finance_required": "yes",
            "exchange_required": 1,
            "exchange_car_details": "2019 Maruti Brezza",
            "notes": "Timeline: 0-15 days | Finance: yes"
        }
        res = self.client.post("/api/inquiries", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data["success"])
        inquiry_id = data["inquiry_id"]

        # Verify it appears in dealer's leads with timeline and finance_required
        leads_res = self.client.get("/api/dealer/inquiries/1")
        self.assertEqual(leads_res.status_code, 200)
        leads = leads_res.json()
        matching_lead = next((l for l in leads if l["id"] == inquiry_id), None)
        self.assertIsNotNone(matching_lead)
        self.assertEqual(matching_lead["buying_timeline"], "0-15 days")
        self.assertEqual(matching_lead["finance_required"], "yes")

        # Update status
        status_res = self.client.post("/api/dealer/inquiry/status", json={
            "inquiry_id": inquiry_id,
            "status": "CONTACTED"
        })
        self.assertEqual(status_res.status_code, 200)

    def test_stock_update_from_dealer(self):
        update_payload = {
            "inventory_id": 1,
            "status": "IN_STOCK",
            "units_available": 5,
            "waiting_period_weeks": 0,
            "colors_available": "Stealth Black (3), Everest White (2)",
            "test_drive_available": 1,
            "promo_note": "Special test update note"
        }
        res = self.client.post("/api/dealer/inventory/update", json=update_payload)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()["success"])

    def test_all_brands_inventory_and_lead_options(self):
        # 1. Verify stock exists for all 6 brands
        brands = ["Tata Motors", "Mahindra", "Hyundai", "Kia", "Toyota", "Maruti Suzuki"]
        for b in brands:
            res = self.client.get(f"/api/inventory?brand={b}")
            self.assertEqual(res.status_code, 200)
            items = res.json()
            self.assertGreater(len(items), 0, f"Expected stock for brand {b}")
            for item in items:
                self.assertTrue(b.lower() in item["car_brand"].lower() or b.lower() in item["dealer_brand"].lower())

        # 2. Test timeline options (0-15 days, 15 - 30 days, 30 - 60 days, just enquiring)
        # and finance options (yes, no, not decided yet)
        test_combinations = [
            ("0-15 days", "yes"),
            ("15 - 30 days", "no"),
            ("30 - 60 days", "not decided yet"),
            ("just enquiring", "not decided yet")
        ]
        for timeline, finance in test_combinations:
            payload = {
                "dealership_id": 2,
                "customer_name": f"Buyer {timeline}",
                "customer_phone": "9876543210",
                "customer_city": "Rudrapur",
                "buying_timeline": timeline,
                "finance_required": finance
            }
            res = self.client.post("/api/inquiries", json=payload)
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertTrue(data["success"])
            inq_id = data["inquiry_id"]

            # Verify in dealer leads
            leads = self.client.get("/api/dealer/inquiries/2").json()
            lead = next((l for l in leads if l["id"] == inq_id), None)
            self.assertIsNotNone(lead)
            self.assertEqual(lead["buying_timeline"], timeline)
            self.assertEqual(lead["finance_required"], finance)

    def test_google_sheets_integration(self):
        from app.sheets_sync import parse_google_sheets_url, parse_csv_records, sync_inventory_from_records

        # 1. Test URL parsing
        test_url = "https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit?gid=456#gid=456"
        csv_url = parse_google_sheets_url(test_url)
        self.assertIn("/export?format=csv", csv_url)
        self.assertIn("1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms", csv_url)

        # 2. Test Template CSV download endpoint includes Brand
        template_res = self.client.get("/api/admin/sheets/template.csv")
        self.assertEqual(template_res.status_code, 200)
        self.assertIn("Brand,Dealership,City,Model,Variant", template_res.text)

        # 3. Test Config endpoint (Auth required)
        unauth_config = self.client.get("/api/admin/sheets/config")
        self.assertEqual(unauth_config.status_code, 401)

        # Authenticate
        login_res = self.client.post("/api/admin/login", json={
            "username": "admin",
            "password": "scoutmycar2026"
        })
        cookies = login_res.cookies

        # Save config
        save_res = self.client.post("/api/admin/sheets/config", json={
            "google_sheet_url": test_url
        }, cookies=cookies)
        self.assertEqual(save_res.status_code, 200)

        # Read config
        config_res = self.client.get("/api/admin/sheets/config", cookies=cookies)
        self.assertEqual(config_res.status_code, 200)
        self.assertEqual(config_res.json()["google_sheet_url"], test_url)

        # 4. Test Multi-Brand CSV records sync into database
        mock_csv = """Brand,Dealership,City,Model,Variant,Fuel,Transmission,Status,Units,WaitingWeeks,Colors,PromoNote
Tata Motors,Gola Ganapati Motors,Haldwani,Tata Nexon,Creative Plus,Petrol,Manual,IN_STOCK,4,0,Daytona Grey,Showroom floor unit.
Toyota,Trust Toyota,Rudrapur,Toyota Urban Cruiser Hyryder,G Strong Hybrid,Hybrid,Automatic,IN_STOCK,2,0,Cafe White,Immediate delivery.
"""
        records = parse_csv_records(mock_csv)
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["brand"], "Tata Motors")
        self.assertEqual(records[0]["model"], "Tata Nexon")
        self.assertEqual(records[0]["units"], 4)

        sync_res = sync_inventory_from_records(records)
        self.assertTrue(sync_res["success"])
        self.assertEqual(sync_res["updated_count"], 2)

        # Verify items now appear in public inventory API
        inv_res = self.client.get("/api/inventory")
        items = inv_res.json()
        self.assertEqual(len(items), 2)
        self.assertTrue(any(i["variant_name"] == "Creative Plus" and i["units_available"] == 4 for i in items))

if __name__ == "__main__":
    unittest.main()
