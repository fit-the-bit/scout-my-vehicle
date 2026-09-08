from pydantic import BaseModel, Field
from typing import Optional

class InquiryCreate(BaseModel):
    dealership_id: Optional[int] = 1
    car_id: Optional[int] = None
    variant_id: Optional[int] = None
    customer_name: str
    customer_phone: str
    customer_email: Optional[str] = None
    customer_city: Optional[str] = "Haldwani"
    inquiry_type: Optional[str] = "availability_check" # 'availability_check', 'test_drive', 'price_quote', 'instant_booking'
    preferred_date: Optional[str] = None
    preferred_time: Optional[str] = None
    buying_timeline: Optional[str] = None # '0-15 days', '15 - 30 days', '30 - 60 days', 'just enquiring'
    finance_required: Optional[str] = None # 'yes', 'no', 'not decided yet'
    exchange_required: Optional[int] = 0
    exchange_car_details: Optional[str] = None
    notes: Optional[str] = None

class StockAlertCreate(BaseModel):
    customer_name: str
    customer_phone: str
    car_id: int
    preferred_city: str = "Haldwani"
    preferred_color: Optional[str] = None

class InventoryUpdate(BaseModel):
    inventory_id: int
    status: str # 'IN_STOCK', 'IN_TRANSIT', 'WAITLIST'
    units_available: int = 0
    waiting_period_weeks: int = 0
    colors_available: Optional[str] = None
    test_drive_available: int = 1
    promo_note: Optional[str] = None

class InquiryStatusUpdate(BaseModel):
    inquiry_id: int
    status: str # 'NEW', 'CONTACTED', 'TEST_DRIVE_DONE', 'CLOSED'

class AdminLoginRequest(BaseModel):
    username: str
    password: str
    next_url: Optional[str] = "/dealer"

class SheetsConfigRequest(BaseModel):
    google_sheet_url: str

class SheetsSyncRequest(BaseModel):
    google_sheet_url: Optional[str] = None
