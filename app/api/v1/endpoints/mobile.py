from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
from sqlalchemy import func

from app.core.dependencies import get_db, get_current_active_user, require_permission
from app.db.models.models import User
from app.db.models.event import Event, EventRegistration, EventStatus, EventCategory, Attendance
from app.db.models.payment import Payment, PaymentStatus
from app.db.models.notification import Notification, NotificationStatus
from app.schemas.event import EventList, EventOut
from app.schemas.payment import PaymentResponse, PaymentAnalytics
from app.schemas.notification import NotificationResponse
from app.services.event_service import EventService
from app.services.payment_service import PaymentService
from app.services.notification_service import NotificationService
from app.services.attendance_service import AttendanceService
from pydantic import BaseModel

router = APIRouter(prefix="/mobile", tags=["Mobile API"])

# Service instances
event_service = EventService()
payment_service = PaymentService()
notification_service = NotificationService()
attendance_service = AttendanceService()

# Mobile-specific response models
class MobileEventList(BaseModel):
    events: List[EventList]
    total_count: int
    has_more: bool
    next_page: Optional[int]

class MobileDashboard(BaseModel):
    upcoming_events: List[EventList]
    recent_activities: List[Dict[str, Any]]
    unread_notifications: int
    total_registrations: int
    total_attendances: int

class MobileEventDetail(BaseModel):
    event: EventOut
    is_registered: bool
    registration_status: Optional[str]
    attendance_status: Optional[str]
    payment_status: Optional[str]
    qr_code_url: Optional[str]

@router.get("/dashboard", response_model=MobileDashboard)
async def get_mobile_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get mobile dashboard data"""
    try:
        # Get upcoming events (next 30 days)
        upcoming_event_objects = event_service.get_upcoming_events(db, limit=5)
        upcoming_events = []
        for event in upcoming_event_objects:
            upcoming_events.append(EventList(
                id=event.id,
                title=event.title,
                short_description=event.short_description,
                category=event.category,
                status=event.status,
                start_date=event.start_date,
                start_time=event.start_time,
                location=event.location,
                city=event.city,
                is_online=event.is_online,
                price=event.price,
                is_free=event.is_free,
                flyer_url=event.flyer_url,
                organizer_name=event.organizer_name,
                current_registrations=event.current_registrations,
                max_capacity=event.max_capacity,
                views_count=event.views_count,
                likes_count=event.likes_count,
                created_at=event.created_at
            ))
        
        # Get recent activities
        recent_activities = []
        
        # Recent registrations
        recent_registrations = db.query(EventRegistration).filter(
            EventRegistration.user_id == current_user.id
        ).order_by(EventRegistration.created_at.desc()).limit(5).all()
        
        for reg in recent_registrations:
            event = db.query(Event).filter(Event.id == reg.event_id).first()
            if event:
                recent_activities.append({
                    "type": "registration",
                    "title": f"Registered for {event.title}",
                    "timestamp": reg.created_at,
                    "event_id": event.id
                })
        
        # Recent attendances
        recent_attendances = db.query(Attendance).filter(
            Attendance.user_id == current_user.id,
            Attendance.check_in_time.isnot(None)
        ).order_by(Attendance.check_in_time.desc()).limit(5).all()
        
        for att in recent_attendances:
            event = db.query(Event).filter(Event.id == att.event_id).first()
            if event:
                recent_activities.append({
                    "type": "attendance",
                    "title": f"Attended {event.title}",
                    "timestamp": att.check_in_time,
                    "event_id": event.id
                })
        
        # Sort activities by timestamp
        recent_activities.sort(key=lambda x: x["timestamp"], reverse=True)
        recent_activities = recent_activities[:10]  # Limit to 10 most recent
        
        # Get unread notifications count
        unread_count = notification_service.get_unread_count(db, current_user.id)
        
        # Get total registrations and attendances
        total_registrations = db.query(EventRegistration).filter(
            EventRegistration.user_id == current_user.id
        ).count()
        
        total_attendances = db.query(Attendance).filter(
            Attendance.user_id == current_user.id,
            Attendance.check_in_time.isnot(None)
        ).count()
        
        return MobileDashboard(
            upcoming_events=upcoming_events,
            recent_activities=recent_activities,
            unread_notifications=unread_count,
            total_registrations=total_registrations,
            total_attendances=total_attendances
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/events", response_model=MobileEventList)
async def get_mobile_events(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=50, description="Items per page"),
    category: Optional[EventCategory] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    status: Optional[EventStatus] = Query(None, description="Filter by status"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get events for mobile app with pagination and filters"""
    try:
        offset = (page - 1) * limit
        
        # Build query
        query = db.query(Event).filter(Event.is_active == True)
        
        if category:
            query = query.filter(Event.category == category)
        
        if status:
            query = query.filter(Event.status == status)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Event.title.ilike(search_term)) |
                (Event.description.ilike(search_term)) |
                (Event.short_description.ilike(search_term))
            )
        
        # Get total count
        total_count = query.count()
        
        # Get paginated results
        events = query.order_by(Event.start_date.asc()).offset(offset).limit(limit).all()
        
        # Convert to response format
        event_list = []
        for event in events:
            event_list.append(EventList(
                id=event.id,
                title=event.title,
                short_description=event.short_description,
                category=event.category,
                status=event.status,
                start_date=event.start_date,
                start_time=event.start_time,
                location=event.location,
                city=event.city,
                is_online=event.is_online,
                price=event.price,
                is_free=event.is_free,
                flyer_url=event.flyer_url,
                organizer_name=event.organizer_name,
                current_registrations=event.current_registrations,
                max_capacity=event.max_capacity,
                views_count=event.views_count,
                likes_count=event.likes_count,
                created_at=event.created_at
            ))
        
        # Check if there are more pages
        has_more = (offset + limit) < total_count
        next_page = page + 1 if has_more else None
        
        return MobileEventList(
            events=event_list,
            total_count=total_count,
            has_more=has_more,
            next_page=next_page
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/events/{event_id}", response_model=MobileEventDetail)
async def get_mobile_event_detail(
    event_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get detailed event information for mobile app"""
    try:
        # Get event
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        # Check registration status
        registration = db.query(EventRegistration).filter(
            EventRegistration.event_id == event_id,
            EventRegistration.user_id == current_user.id
        ).first()
        
        is_registered = registration is not None
        registration_status = registration.status if registration else None
        
        # Check attendance status
        attendance = db.query(Attendance).filter(
            Attendance.event_id == event_id,
            Attendance.user_id == current_user.id
        ).first()
        
        attendance_status = None
        if attendance:
            if attendance.check_in_time:
                attendance_status = "checked_in"
            elif attendance.check_out_time:
                attendance_status = "checked_out"
        
        # Check payment status
        payment_status = None
        if registration:
            payment = db.query(Payment).filter(
                Payment.registration_id == registration.id
            ).first()
            if payment:
                payment_status = payment.payment_status.value
        
        # Get QR code URL if event is ongoing and user is registered
        qr_code_url = None
        if (is_registered and 
            event.status == EventStatus.ONGOING and 
            attendance and 
            not attendance.check_in_time):
            qr_code_url = f"/api/v1/attendance/events/{event_id}/qr/check-in"
        
        # Convert event to detail format
        event_detail = EventOut(
            id=event.id,
            title=event.title,
            description=event.description,
            short_description=event.short_description,
            category=event.category,
            status=event.status,
            start_date=event.start_date,
            end_date=event.end_date,
            start_time=event.start_time,
            end_time=event.end_time,
            location=event.location,
            address=event.address,
            city=event.city,
            country=event.country,
            is_online=event.is_online,
            online_url=event.online_url,
            max_capacity=event.max_capacity,
            current_registrations=event.current_registrations,
            price=event.price,
            currency=event.currency,
            is_free=event.is_free,
            flyer_url=event.flyer_url,
            banner_url=event.banner_url,
            organizer_name=event.organizer_name,
            organizer_email=event.organizer_email,
            organizer_phone=event.organizer_phone,
            is_featured=event.is_featured,
            views_count=event.views_count,
            likes_count=event.likes_count,
            created_at=event.created_at,
            updated_at=event.updated_at
        )
        
        return MobileEventDetail(
            event=event_detail,
            is_registered=is_registered,
            registration_status=registration_status,
            attendance_status=attendance_status,
            payment_status=payment_status,
            qr_code_url=qr_code_url
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/my-events", response_model=List[MobileEventDetail])
async def get_my_events(
    status: Optional[str] = Query(None, description="Filter by registration status"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's registered events"""
    try:
        # Get user's registrations
        query = db.query(EventRegistration).filter(
            EventRegistration.user_id == current_user.id
        )
        
        if status:
            query = query.filter(EventRegistration.status == status)
        
        registrations = query.all()
        
        result = []
        for registration in registrations:
            event = db.query(Event).filter(Event.id == registration.event_id).first()
            if event:
                # Get attendance status
                attendance = db.query(Attendance).filter(
                    Attendance.event_id == event.id,
                    Attendance.user_id == current_user.id
                ).first()
                
                attendance_status = None
                if attendance:
                    if attendance.check_in_time:
                        attendance_status = "checked_in"
                    elif attendance.check_out_time:
                        attendance_status = "checked_out"
                
                # Get payment status
                payment = db.query(Payment).filter(
                    Payment.registration_id == registration.id
                ).first()
                payment_status = payment.payment_status.value if payment else None
                
                # Convert to response format
                event_detail = EventOut(
                    id=event.id,
                    title=event.title,
                    description=event.description,
                    short_description=event.short_description,
                    category=event.category,
                    status=event.status,
                    start_date=event.start_date,
                    end_date=event.end_date,
                    start_time=event.start_time,
                    end_time=event.end_time,
                    location=event.location,
                    address=event.address,
                    city=event.city,
                    country=event.country,
                    is_online=event.is_online,
                    online_url=event.online_url,
                    max_capacity=event.max_capacity,
                    current_registrations=event.current_registrations,
                    price=event.price,
                    currency=event.currency,
                    is_free=event.is_free,
                    flyer_url=event.flyer_url,
                    banner_url=event.banner_url,
                    organizer_name=event.organizer_name,
                    organizer_email=event.organizer_email,
                    organizer_phone=event.organizer_phone,
                    is_featured=event.is_featured,
                    views_count=event.views_count,
                    likes_count=event.likes_count,
                    created_at=event.created_at,
                    updated_at=event.updated_at
                )
                
                result.append(MobileEventDetail(
                    event=event_detail,
                    is_registered=True,
                    registration_status=registration.status,
                    attendance_status=attendance_status,
                    payment_status=payment_status,
                    qr_code_url=None
                ))
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/notifications", response_model=List[NotificationResponse])
async def get_mobile_notifications(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=50, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user notifications for mobile app"""
    try:
        offset = (page - 1) * limit
        notifications = notification_service.get_user_notifications(
            db, current_user.id, limit=limit, offset=offset
        )
        
        # Convert to response format
        notification_list = []
        for notification in notifications:
            notification_list.append(NotificationResponse(
                id=notification.notification_id,
                title=notification.title,
                message=notification.message,
                type=notification.notification_type.value,
                priority=notification.priority.value,
                status=notification.status.value,
                action_url=notification.action_url,
                created_at=notification.created_at,
                read_at=notification.read_at
            ))
        
        return notification_list
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark notification as read"""
    try:
        success = notification_service.mark_notification_read(
            db, notification_id, current_user.id
        )
        
        if success:
            return {"message": "Notification marked as read"}
        else:
            raise HTTPException(status_code=404, detail="Notification not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/payments", response_model=List[PaymentResponse])
async def get_mobile_payments(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=50, description="Items per page"),
    status: Optional[PaymentStatus] = Query(None, description="Filter by payment status"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's payment history for mobile app"""
    try:
        offset = (page - 1) * limit
        
        # Build query
        query = db.query(Payment).filter(Payment.user_id == current_user.id)
        
        if status:
            query = query.filter(Payment.payment_status == status)
        
        # Get paginated results
        payments = query.order_by(Payment.created_at.desc()).offset(offset).limit(limit).all()
        
        # Convert to response format
        payment_list = []
        for payment in payments:
            payment_list.append(PaymentResponse(
                id=payment.id,
                payment_id=payment.payment_id,
                amount=payment.amount,
                currency=payment.currency,
                payment_method=payment.payment_method.value,
                payment_status=payment.payment_status.value,
                provider=payment.provider,
                provider_payment_id=payment.provider_payment_id,
                provider_fee=payment.provider_fee,
                user_id=payment.user_id,
                event_id=payment.event_id,
                registration_id=payment.registration_id,
                payment_metadata=json.loads(payment.payment_metadata) if payment.payment_metadata else None,
                created_at=payment.created_at,
                updated_at=payment.updated_at,
                paid_at=payment.paid_at,
                expired_at=payment.expired_at
            ))
        
        return payment_list
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/payments/analytics", response_model=PaymentAnalytics)
async def get_mobile_payment_analytics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get payment analytics for mobile app"""
    try:
        analytics = payment_service.get_payment_analytics(db, current_user.id)
        return PaymentAnalytics(**analytics)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/events/{event_id}/register")
async def register_for_event_mobile(
    event_id: int,
    ticket_type: str = Query(..., description="Ticket type"),
    quantity: int = Query(1, ge=1, le=10, description="Number of tickets"),
    discount_code: Optional[str] = Query(None, description="Discount code"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Register for event from mobile app"""
    try:
        # Check if already registered
        existing_registration = db.query(EventRegistration).filter(
            EventRegistration.event_id == event_id,
            EventRegistration.user_id == current_user.id
        ).first()
        
        if existing_registration:
            raise HTTPException(status_code=400, detail="Already registered for this event")
        
        # Create registration
        registration_data = {
            "ticket_type": ticket_type,
            "quantity": quantity,
            "discount_code": discount_code
        }
        
        registration = event_service.register_for_event(
            db, event_id, current_user.id, registration_data
        )
        
        if not registration:
            raise HTTPException(status_code=400, detail="Registration failed")
        
        return {
            "message": "Registration successful",
            "registration_id": registration.id,
            "status": registration.status
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/attendance/scan-qr")
async def scan_qr_code_mobile(
    qr_data: str = Query(..., description="QR code data"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Scan QR code for attendance from mobile app"""
    try:
        result = attendance_service.scan_qr_code(db, qr_data, current_user.id)
        
        if result["success"]:
            return {
                "message": result["message"],
                "attendance_type": result["attendance_type"],
                "event_id": result["event_id"],
                "timestamp": result["timestamp"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["message"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/profile")
async def get_mobile_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user profile for mobile app"""
    try:
        # Get user statistics
        total_registrations = db.query(EventRegistration).filter(
            EventRegistration.user_id == current_user.id
        ).count()
        
        total_attendances = db.query(Attendance).filter(
            Attendance.user_id == current_user.id,
            Attendance.check_in_time.isnot(None)
        ).count()
        
        total_payments = db.query(Payment).filter(
            Payment.user_id == current_user.id,
            Payment.payment_status == PaymentStatus.SUCCESS
        ).count()
        
        total_spent = db.query(func.sum(Payment.amount)).filter(
            Payment.user_id == current_user.id,
            Payment.payment_status == PaymentStatus.SUCCESS
        ).scalar() or 0
        
        return {
            "user": {
                "id": current_user.id,
                "email": current_user.email,
                "full_name": current_user.full_name,
                "role": current_user.role.name,
                "is_verified": current_user.is_verified,
                "created_at": current_user.created_at
            },
            "statistics": {
                "total_registrations": total_registrations,
                "total_attendances": total_attendances,
                "total_payments": total_payments,
                "total_spent": total_spent
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
