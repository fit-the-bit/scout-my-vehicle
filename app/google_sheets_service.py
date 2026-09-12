import os
import csv
import json
import urllib.request
import urllib.error
from datetime import datetime
from typing import Dict, Any, Optional

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
CSV_FILE_PATH = os.path.join(DATA_DIR, "inquiries_google_sheet.csv")

CSV_HEADERS = [
    "Timestamp",
    "Inquiry ID",
    "Customer Name",
    "Customer Phone",
    "Customer Email",
    "Customer Location",
    "Car Model",
    "Variant Name",
    "Fuel Type",
    "Transmission",
    "Colour",
    "Ex-Showroom Price",
    "Buying Timeline",
    "Finance Required",
    "Preferred Bank",
    "Exchange Required",
    "Exchange Car Details",
    "Notes",
    "Status"
]

def ensure_csv_initialized():
    """Ensures data directory and CSV header row exist."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)
    
    if not os.path.exists(CSV_FILE_PATH):
        with open(CSV_FILE_PATH, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADERS)

def append_inquiry_to_csv(inquiry_data: Dict[str, Any]) -> str:
    """Appends an inquiry record as a new row in inquiries_google_sheet.csv."""
    ensure_csv_initialized()
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    raw_phone = str(inquiry_data.get("customer_phone") or "").strip()
    phone_display = f"'{raw_phone}" if (raw_phone.startswith("+") and not raw_phone.startswith("'")) else raw_phone

    row = [
        timestamp,
        inquiry_data.get("inquiry_id", ""),
        inquiry_data.get("customer_name", ""),
        phone_display,
        inquiry_data.get("customer_email", "") or "N/A",
        inquiry_data.get("customer_city", "") or "Not Specified",
        inquiry_data.get("car_model", "") or "Any Model",
        inquiry_data.get("variant_name", "") or "Standard",
        inquiry_data.get("fuel_type", "") or "N/A",
        inquiry_data.get("transmission", "") or "N/A",
        inquiry_data.get("color", "") or inquiry_data.get("colors_available", "") or "Any",
        inquiry_data.get("price", "") or "N/A",
        inquiry_data.get("buying_timeline", "") or "N/A",
        inquiry_data.get("finance_required", "") or "no",
        inquiry_data.get("preferred_bank", "") or "N/A",
        "Yes" if inquiry_data.get("exchange_required") else "No",
        inquiry_data.get("exchange_car_details", "") or "N/A",
        inquiry_data.get("notes", "") or "",
        "NEW"
    ]
    
    with open(CSV_FILE_PATH, mode="a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(row)
        
    return CSV_FILE_PATH

def forward_to_google_sheet_webhook(webhook_url: str, inquiry_data: Dict[str, Any]) -> bool:
    """
    Sends the inquiry JSON payload to a Google Apps Script Web App URL 
    to append directly into a live Google Sheet.
    """
    if not webhook_url or not webhook_url.startswith("http"):
        return False
        
    raw_phone = str(inquiry_data.get("customer_phone") or "").strip()
    # In Google Sheets, a leading '+' is treated as a mathematical formula, causing a formula parse error (#ERROR!).
    # Prepending a single apostrophe forces Google Sheets to treat the value as plain text and display '+91...' cleanly.
    formatted_phone = f"'{raw_phone}" if (raw_phone and not raw_phone.startswith("'")) else raw_phone

    payload = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "inquiry_id": inquiry_data.get("inquiry_id"),
        "customer_name": inquiry_data.get("customer_name"),
        "customer_phone": formatted_phone,
        "customer_email": inquiry_data.get("customer_email") or "N/A",
        "customer_city": inquiry_data.get("customer_city") or "Not Specified",
        "car_model": inquiry_data.get("car_model") or "Any Model",
        "variant_name": inquiry_data.get("variant_name") or "Standard",
        "fuel_type": inquiry_data.get("fuel_type") or "N/A",
        "transmission": inquiry_data.get("transmission") or "N/A",
        "color": inquiry_data.get("color") or inquiry_data.get("colors_available") or "Any",
        "buying_timeline": inquiry_data.get("buying_timeline") or "N/A",
        "finance_required": inquiry_data.get("finance_required") or "no",
        "preferred_bank": inquiry_data.get("preferred_bank") or "N/A",
        "exchange_car_details": inquiry_data.get("exchange_car_details") or "N/A",
        "notes": inquiry_data.get("notes") or ""
    }
    
    try:
        req_data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            webhook_url,
            data=req_data,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0"
            }
        )
        with urllib.request.urlopen(req, timeout=8) as response:
            return response.status in (200, 201, 302)
    except Exception as e:
        print(f"[GoogleSheetsSync] Webhook forwarding notice: {e}")
        return False

DEFAULT_INQUIRIES_WEBHOOK_URL = os.getenv(
    "GOOGLE_SHEET_INQUIRIES_WEBHOOK",
    "https://script.google.com/macros/s/AKfycbyGjbZe4owqaBoY_m76pQOSxlisjHFbfqxMKhS7FFCbaBr0G3wa3XBNq1h14uyn5nMD/exec"
)

def store_inquiry_in_google_sheet(inquiry_data: Dict[str, Any], webhook_url: Optional[str] = None) -> Dict[str, Any]:
    """
    Primary interface: records inquiry in local Google Sheet CSV file
    and forwards to Google Apps Script Web App if webhook_url is configured.
    """
    csv_path = append_inquiry_to_csv(inquiry_data)
    target_webhook = webhook_url or os.getenv("GOOGLE_SHEET_INQUIRIES_WEBHOOK") or DEFAULT_INQUIRIES_WEBHOOK_URL
    webhook_success = False
    if target_webhook:
        webhook_success = forward_to_google_sheet_webhook(target_webhook, inquiry_data)
        
    return {
        "stored_in_csv": True,
        "csv_path": csv_path,
        "webhook_forwarded": webhook_success
    }

def get_google_apps_script_template() -> str:
    """Returns Google Apps Script deployment code for users to paste into Google Sheets."""
    return """// Google Apps Script to auto-append ScoutMyVehicle enquiries to Google Sheets
function doPost(e) {
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName("Inquiries") || ss.getSheets()[0];
    
    if (sheet.getLastRow() === 0) {
      sheet.appendRow([
        "Timestamp", "Inquiry ID", "Customer Name", "Customer Phone", 
        "Customer Email", "Location", "Car Model", "Variant", 
        "Fuel", "Transmission", "Colour", "Timeline", 
        "Finance Required", "Preferred Bank", "Exchange Details", "Notes"
      ]);
      sheet.getRange(1, 1, 1, 16).setFontWeight("bold").setBackground("#f1f5f9");
      sheet.getRange("D:D").setNumberFormat("@");
    }
    
    var data = JSON.parse(e.postData.contents);
    var rawPhone = (data.customer_phone || "").toString().trim();
    // Prepend single quote if not present to ensure Google Sheets treats it as plain text (prevents #ERROR! formula parse error on +91)
    var phone = rawPhone ? (rawPhone.indexOf("'") === 0 ? rawPhone : "'" + rawPhone) : "";

    sheet.appendRow([
      data.timestamp || new Date(),
      data.inquiry_id || "",
      data.customer_name || "",
      phone,
      data.customer_email || "",
      data.customer_city || "",
      data.car_model || "",
      data.variant_name || "",
      data.fuel_type || "",
      data.transmission || "",
      data.color || "",
      data.buying_timeline || "",
      data.finance_required || "",
      data.preferred_bank || "",
      data.exchange_car_details || "",
      data.notes || ""
    ]);

    var lastRow = sheet.getLastRow();
    sheet.getRange(lastRow, 4).setNumberFormat("@");
    
    return ContentService.createTextOutput(JSON.stringify({
      status: "success", 
      message: "Inquiry appended successfully", 
      sheet_name: sheet.getName(),
      row: lastRow
    })).setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({status: "error", message: err.toString()}))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function doGet(e) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName("Inquiries") || ss.getSheets()[0];
  return ContentService.createTextOutput(JSON.stringify({
    status: "online",
    service: "ScoutMyVehicle Google Sheets Webhook",
    active_sheet: sheet.getName(),
    total_rows: sheet.getLastRow(),
    timestamp: new Date()
  })).setMimeType(ContentService.MimeType.JSON);
}
"""
