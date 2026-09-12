/**
 * ScoutMyVehicle - Google Sheets Webhook Script
 * 
 * INSTRUCTIONS TO DEPLOY:
 * 1. Open your Google Sheet.
 * 2. Click 'Extensions' > 'Apps Script'.
 * 3. Replace any code in the editor with this script.
 * 4. Click 'Deploy' > 'New deployment'.
 * 5. Select type: 'Web app'.
 * 6. Set:
 *    - Execute as: 'Me'
 *    - Who has access: 'Anyone'
 * 7. Click 'Deploy', copy the Web App URL (starts with https://script.google.com/macros/s/...)
 * 8. In ScoutMyVehicle dealer portal or .env, save this URL as GOOGLE_SHEET_INQUIRIES_WEBHOOK.
 */

function doPost(e) {
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName('Inquiries') || ss.getSheets()[0];
    
    // Auto-create bold header row if new sheet
    if (sheet.getLastRow() === 0) {
      sheet.appendRow([
        'Timestamp', 'Inquiry ID', 'Customer Name', 'Customer Phone', 
        'Customer Email', 'Location', 'Car Model', 'Variant', 
        'Fuel', 'Transmission', 'Colour', 'Timeline', 
        'Finance Required', 'Preferred Bank', 'Exchange Details', 'Notes'
      ]);
      sheet.getRange(1, 1, 1, 16).setFontWeight('bold').setBackground('#f1f5f9');
      sheet.getRange('D:D').setNumberFormat('@');
    }
    
    var data = JSON.parse(e.postData.contents);
    var rawPhone = (data.customer_phone || '').toString().trim();
    // Prepend single quote if not present to ensure Google Sheets treats it as plain text (prevents #ERROR! formula parse error on +91)
    var phone = rawPhone ? (rawPhone.indexOf("'") === 0 ? rawPhone : "'" + rawPhone) : '';

    sheet.appendRow([
      data.timestamp || new Date(),
      data.inquiry_id || '',
      data.customer_name || '',
      phone,
      data.customer_email || '',
      data.customer_city || '',
      data.car_model || '',
      data.variant_name || '',
      data.fuel_type || '',
      data.transmission || '',
      data.color || '',
      data.buying_timeline || '',
      data.finance_required || '',
      data.preferred_bank || '',
      data.exchange_car_details || '',
      data.notes || ''
    ]);

    var lastRow = sheet.getLastRow();
    sheet.getRange(lastRow, 4).setNumberFormat('@');
    
    return ContentService.createTextOutput(JSON.stringify({ 
      status: 'success', 
      message: 'Inquiry appended successfully',
      sheet_name: sheet.getName(),
      row: lastRow 
    })).setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({ status: 'error', message: err.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function doGet(e) {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sheet = ss.getSheetByName('Inquiries') || ss.getSheets()[0];
  return ContentService.createTextOutput(JSON.stringify({
    status: 'online',
    service: 'ScoutMyVehicle Google Sheets Webhook',
    active_sheet: sheet.getName(),
    total_rows: sheet.getLastRow(),
    timestamp: new Date()
  })).setMimeType(ContentService.MimeType.JSON);
}