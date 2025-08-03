from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class QRCodeResponse(BaseModel):
    qr_code_data: str
    qr_code_image: str  # Base64 encoded image
    expires_at: Optional[datetime] = None

class ScanQRRequest(BaseModel):
    qr_code: str
    event_id: int

class AttendanceCreate(BaseModel):
    event_id: int
    user_id: int
    notes: Optional[str] = None

class AttendanceUpdate(BaseModel):
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    notes: Optional[str] = None

class AttendanceOut(BaseModel):
    id: int
    event_id: int
    user_id: int
    user_name: str
    user_email: str
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    check_in_qr_scanned: bool
    check_out_qr_scanned: bool
    notes: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class EventAttendanceStatus(BaseModel):
    event_id: int
    event_title: str
    total_registered: int
    total_checked_in: int
    total_checked_out: int
    check_in_started: bool
    check_out_started: bool

class AttendanceSummary(BaseModel):
    event_id: int
    event_title: str
    attendances: List[AttendanceOut]
    summary: EventAttendanceStatus
