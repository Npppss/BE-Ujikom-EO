from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.schemas.attendance import (
    QRCodeResponse, ScanQRRequest, AttendanceOut, 
    EventAttendanceStatus, AttendanceSummary
)
from app.services.attendance_service import attendance_service
from app.core.dependencies import get_current_active_user, require_permission
from app.db.models import User

router = APIRouter(prefix="/attendance", tags=["Attendance"])

# Organizer/Admin endpoints for managing attendance

@router.post("/events/{event_id}/start-check-in")
def start_check_in(
    event_id: int,
    current_user: User = Depends(require_permission("event:update")),
    db: Session = Depends(get_db)
):
    """Start check-in process for an event (Organizer/Admin only)"""
    try:
        success = attendance_service.start_check_in(db, event_id)
        return {"message": "Check-in process started successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/events/{event_id}/stop-check-in")
def stop_check_in(
    event_id: int,
    current_user: User = Depends(require_permission("event:update")),
    db: Session = Depends(get_db)
):
    """Stop check-in process for an event (Organizer/Admin only)"""
    try:
        success = attendance_service.stop_check_in(db, event_id)
        return {"message": "Check-in process stopped successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/events/{event_id}/start-check-out")
def start_check_out(
    event_id: int,
    current_user: User = Depends(require_permission("event:update")),
    db: Session = Depends(get_db)
):
    """Start check-out process for an event (Organizer/Admin only)"""
    try:
        success = attendance_service.start_check_out(db, event_id)
        return {"message": "Check-out process started successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/events/{event_id}/stop-check-out")
def stop_check_out(
    event_id: int,
    current_user: User = Depends(require_permission("event:update")),
    db: Session = Depends(get_db)
):
    """Stop check-out process for an event (Organizer/Admin only)"""
    try:
        success = attendance_service.stop_check_out(db, event_id)
        return {"message": "Check-out process stopped successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# QR Code generation endpoints

@router.get("/events/{event_id}/qr/check-in", response_model=QRCodeResponse)
def get_check_in_qr(
    event_id: int,
    current_user: User = Depends(require_permission("event:read")),
    db: Session = Depends(get_db)
):
    """Generate check-in QR code for an event (Organizer/Admin only)"""
    try:
        qr_data = attendance_service.generate_check_in_qr(db, event_id)
        return QRCodeResponse(
            qr_code_data=qr_data["qr_code_data"],
            qr_code_image=qr_data["qr_code_image"]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/events/{event_id}/qr/check-out", response_model=QRCodeResponse)
def get_check_out_qr(
    event_id: int,
    current_user: User = Depends(require_permission("event:read")),
    db: Session = Depends(get_db)
):
    """Generate check-out QR code for an event (Organizer/Admin only)"""
    try:
        qr_data = attendance_service.generate_check_out_qr(db, event_id)
        return QRCodeResponse(
            qr_code_data=qr_data["qr_code_data"],
            qr_code_image=qr_data["qr_code_image"]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# QR Code scanning endpoints (for users)

@router.post("/scan/check-in")
def scan_check_in_qr(
    request: ScanQRRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Scan check-in QR code (for users)"""
    try:
        result = attendance_service.scan_check_in_qr(db, request.qr_code, current_user.id)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/scan/check-out")
def scan_check_out_qr(
    request: ScanQRRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Scan check-out QR code (for users)"""
    try:
        result = attendance_service.scan_check_out_qr(db, request.qr_code, current_user.id)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Attendance reporting endpoints

@router.get("/events/{event_id}/list", response_model=List[AttendanceOut])
def get_event_attendance(
    event_id: int,
    current_user: User = Depends(require_permission("event:read")),
    db: Session = Depends(get_db)
):
    """Get attendance list for an event (Organizer/Admin only)"""
    try:
        attendances = attendance_service.get_event_attendance(db, event_id)
        return attendances
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/events/{event_id}/summary", response_model=EventAttendanceStatus)
def get_attendance_summary(
    event_id: int,
    current_user: User = Depends(require_permission("event:read")),
    db: Session = Depends(get_db)
):
    """Get attendance summary for an event (Organizer/Admin only)"""
    try:
        summary = attendance_service.get_attendance_summary(db, event_id)
        return summary
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/my-attendance")
def get_my_attendance(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's attendance history"""
    try:
        attendances = attendance_service.get_user_attendance(db, current_user.id)
        return {"attendances": attendances}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Alternative QR scanning endpoint (for mobile apps)

@router.post("/scan/qr")
def scan_qr_code(
    request: ScanQRRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Universal QR code scanner that detects check-in or check-out automatically"""
    try:
        # Try check-in first
        try:
            result = attendance_service.scan_check_in_qr(db, request.qr_code, current_user.id)
            return {"type": "check_in", **result}
        except Exception as check_in_error:
            # If check-in fails, try check-out
            try:
                result = attendance_service.scan_check_out_qr(db, request.qr_code, current_user.id)
                return {"type": "check_out", **result}
            except Exception as check_out_error:
                # If both fail, return the more specific error
                if "Check-in is not started" in str(check_in_error):
                    raise check_in_error
                elif "Check-out is not started" in str(check_out_error):
                    raise check_out_error
                else:
                    raise HTTPException(status_code=400, detail="Invalid QR code")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
