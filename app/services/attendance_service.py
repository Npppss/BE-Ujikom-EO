from sqlalchemy.orm import Session
from app.db.models import Event, Attendance, User
from app.services.qr_service import qr_service
from datetime import datetime
from typing import List, Optional
import uuid

class AttendanceService:
    def __init__(self):
        pass
    
    def start_check_in(self, db: Session, event_id: int) -> bool:
        """Start check-in process for an event"""
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise Exception("Event not found")
        
        event.check_in_started = True
        db.commit()
        return True
    
    def start_check_out(self, db: Session, event_id: int) -> bool:
        """Start check-out process for an event"""
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise Exception("Event not found")
        
        event.check_out_started = True
        db.commit()
        return True
    
    def stop_check_in(self, db: Session, event_id: int) -> bool:
        """Stop check-in process for an event"""
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise Exception("Event not found")
        
        event.check_in_started = False
        db.commit()
        return True
    
    def stop_check_out(self, db: Session, event_id: int) -> bool:
        """Stop check-out process for an event"""
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise Exception("Event not found")
        
        event.check_out_started = False
        db.commit()
        return True
    
    def generate_check_in_qr(self, db: Session, event_id: int) -> dict:
        """Generate check-in QR code for an event"""
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise Exception("Event not found")
        
        # Generate new QR code if needed
        if not event.check_in_qr_code:
            event.check_in_qr_code = str(uuid.uuid4())
            db.commit()
        
        # Generate QR code data
        qr_data = qr_service.generate_check_in_qr_data(event_id, event.check_in_qr_code)
        qr_image = qr_service.generate_qr_code(qr_data)
        
        return {
            "qr_code_data": qr_data,
            "qr_code_image": qr_image,
            "qr_code": event.check_in_qr_code
        }
    
    def generate_check_out_qr(self, db: Session, event_id: int) -> dict:
        """Generate check-out QR code for an event"""
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise Exception("Event not found")
        
        # Generate new QR code if needed
        if not event.check_out_qr_code:
            event.check_out_qr_code = str(uuid.uuid4())
            db.commit()
        
        # Generate QR code data
        qr_data = qr_service.generate_check_out_qr_data(event_id, event.check_out_qr_code)
        qr_image = qr_service.generate_qr_code(qr_data)
        
        return {
            "qr_code_data": qr_data,
            "qr_code_image": qr_image,
            "qr_code": event.check_out_qr_code
        }
    
    def scan_check_in_qr(self, db: Session, qr_data: str, user_id: int) -> dict:
        """Scan check-in QR code and record attendance"""
        # Parse QR data
        parsed_data = qr_service.parse_qr_data(qr_data)
        if not parsed_data:
            raise Exception("Invalid QR code data")
        
        event_id = parsed_data.get("event_id")
        qr_code = parsed_data.get("qr_code")
        
        # Validate QR code
        if not qr_service.validate_qr_code(parsed_data, event_id, "check_in"):
            raise Exception("Invalid or expired QR code")
        
        # Check if event exists and check-in is started
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise Exception("Event not found")
        
        if not event.check_in_started:
            raise Exception("Check-in is not started for this event")
        
        if event.check_in_qr_code != qr_code:
            raise Exception("Invalid QR code for this event")
        
        # Check if user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise Exception("User not found")
        
        # Check if attendance record exists
        attendance = db.query(Attendance).filter(
            Attendance.event_id == event_id,
            Attendance.user_id == user_id
        ).first()
        
        if not attendance:
            # Create new attendance record
            attendance = Attendance(
                event_id=event_id,
                user_id=user_id
            )
            db.add(attendance)
        
        # Check if already checked in
        if attendance.check_in_qr_scanned:
            raise Exception("Already checked in for this event")
        
        # Record check-in
        attendance.check_in_time = datetime.utcnow()
        attendance.check_in_qr_scanned = True
        db.commit()
        
        return {
            "message": "Check-in successful",
            "check_in_time": attendance.check_in_time,
            "user_name": user.full_name,
            "event_title": event.title
        }
    
    def scan_check_out_qr(self, db: Session, qr_data: str, user_id: int) -> dict:
        """Scan check-out QR code and record attendance"""
        # Parse QR data
        parsed_data = qr_service.parse_qr_data(qr_data)
        if not parsed_data:
            raise Exception("Invalid QR code data")
        
        event_id = parsed_data.get("event_id")
        qr_code = parsed_data.get("qr_code")
        
        # Validate QR code
        if not qr_service.validate_qr_code(parsed_data, event_id, "check_out"):
            raise Exception("Invalid or expired QR code")
        
        # Check if event exists and check-out is started
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise Exception("Event not found")
        
        if not event.check_out_started:
            raise Exception("Check-out is not started for this event")
        
        if event.check_out_qr_code != qr_code:
            raise Exception("Invalid QR code for this event")
        
        # Check if user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise Exception("User not found")
        
        # Check if attendance record exists
        attendance = db.query(Attendance).filter(
            Attendance.event_id == event_id,
            Attendance.user_id == user_id
        ).first()
        
        if not attendance:
            raise Exception("No attendance record found. Please check in first.")
        
        # Check if already checked out
        if attendance.check_out_qr_scanned:
            raise Exception("Already checked out for this event")
        
        # Record check-out
        attendance.check_out_time = datetime.utcnow()
        attendance.check_out_qr_scanned = True
        db.commit()
        
        return {
            "message": "Check-out successful",
            "check_out_time": attendance.check_out_time,
            "user_name": user.full_name,
            "event_title": event.title
        }
    
    def get_event_attendance(self, db: Session, event_id: int) -> List[dict]:
        """Get attendance list for an event"""
        attendances = db.query(Attendance).filter(Attendance.event_id == event_id).all()
        
        result = []
        for attendance in attendances:
            user = db.query(User).filter(User.id == attendance.user_id).first()
            result.append({
                "id": attendance.id,
                "user_id": attendance.user_id,
                "user_name": user.full_name if user else "Unknown",
                "user_email": user.email if user else "Unknown",
                "check_in_time": attendance.check_in_time,
                "check_out_time": attendance.check_out_time,
                "check_in_qr_scanned": attendance.check_in_qr_scanned,
                "check_out_qr_scanned": attendance.check_out_qr_scanned,
                "notes": attendance.notes,
                "created_at": attendance.created_at
            })
        
        return result
    
    def get_attendance_summary(self, db: Session, event_id: int) -> dict:
        """Get attendance summary for an event"""
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise Exception("Event not found")
        
        attendances = db.query(Attendance).filter(Attendance.event_id == event_id).all()
        
        total_registered = len(attendances)
        total_checked_in = sum(1 for a in attendances if a.check_in_qr_scanned)
        total_checked_out = sum(1 for a in attendances if a.check_out_qr_scanned)
        
        return {
            "event_id": event_id,
            "event_title": event.title,
            "total_registered": total_registered,
            "total_checked_in": total_checked_in,
            "total_checked_out": total_checked_out,
            "check_in_started": event.check_in_started,
            "check_out_started": event.check_out_started
        }
    
    def get_user_attendance(self, db: Session, user_id: int) -> List[dict]:
        """Get attendance history for a user"""
        attendances = db.query(Attendance).filter(Attendance.user_id == user_id).all()
        
        result = []
        for attendance in attendances:
            event = db.query(Event).filter(Event.id == attendance.event_id).first()
            result.append({
                "id": attendance.id,
                "event_id": attendance.event_id,
                "event_title": event.title if event else "Unknown Event",
                "check_in_time": attendance.check_in_time,
                "check_out_time": attendance.check_out_time,
                "check_in_qr_scanned": attendance.check_in_qr_scanned,
                "check_out_qr_scanned": attendance.check_out_qr_scanned,
                "notes": attendance.notes,
                "created_at": attendance.created_at
            })
        
        return result

# Create service instance
attendance_service = AttendanceService() 