from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.schemas.event import (
    EventCreate, EventUpdate, EventOut, EventList, EventRegistrationCreate,
    EventRegistrationOut, EventLikeCreate, EventLikeOut, EventCommentCreate,
    EventCommentOut, EventAnalytics, EventSearchParams, EventStats
)
from app.services.event_service import event_service
from app.core.dependencies import get_current_active_user, require_permission
from app.db.models import User, EventStatus, EventCategory
from datetime import datetime

router = APIRouter(prefix="/events", tags=["Event Management"])

# Event CRUD Operations

@router.post("/", response_model=EventOut)
def create_event(
    event: EventCreate,
    current_user: User = Depends(require_permission("event:create")),
    db: Session = Depends(get_db)
):
    """Create a new event"""
    try:
        new_event = event_service.create_event(db, event, current_user.id)
        return EventOut(
            id=new_event.id,
            title=new_event.title,
            description=new_event.description,
            short_description=new_event.short_description,
            category=new_event.category,
            status=new_event.status,
            start_date=new_event.start_date,
            end_date=new_event.end_date,
            start_time=new_event.start_time,
            end_time=new_event.end_time,
            location=new_event.location,
            address=new_event.address,
            city=new_event.city,
            country=new_event.country,
            is_online=new_event.is_online,
            online_url=new_event.online_url,
            max_capacity=new_event.max_capacity,
            current_registrations=new_event.current_registrations,
            price=new_event.price,
            currency=new_event.currency,
            is_free=new_event.is_free,
            flyer_url=new_event.flyer_url,
            banner_url=new_event.banner_url,
            gallery_urls=new_event.gallery_urls.split(',') if new_event.gallery_urls else None,
            organizer_name=new_event.organizer_name,
            organizer_email=new_event.organizer_email,
            organizer_phone=new_event.organizer_phone,
            is_featured=new_event.is_featured,
            allow_waitlist=new_event.allow_waitlist,
            require_approval=new_event.require_approval,
            organizer_id=new_event.organizer_id,
            is_active=new_event.is_active,
            views_count=new_event.views_count,
            likes_count=new_event.likes_count,
            shares_count=new_event.shares_count,
            created_at=new_event.created_at,
            updated_at=new_event.updated_at,
            published_at=new_event.published_at
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=dict)
def get_events(
    search: Optional[str] = Query(None, description="Search term"),
    category: Optional[EventCategory] = Query(None, description="Event category"),
    status: Optional[EventStatus] = Query(None, description="Event status"),
    city: Optional[str] = Query(None, description="City filter"),
    is_online: Optional[bool] = Query(None, description="Online event filter"),
    is_free: Optional[bool] = Query(None, description="Free event filter"),
    start_date: Optional[str] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date filter (YYYY-MM-DD)"),
    organizer_id: Optional[int] = Query(None, description="Organizer ID filter"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get events with filtering and pagination"""
    try:
        # Convert date strings to date objects
        start_date_obj = None
        end_date_obj = None
        if start_date:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        if end_date:
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        params = EventSearchParams(
            search=search,
            category=category,
            status=status,
            city=city,
            is_online=is_online,
            is_free=is_free,
            start_date=start_date_obj,
            end_date=end_date_obj,
            organizer_id=organizer_id,
            page=page,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        result = event_service.get_events(db, params)
        
        # Convert events to EventList format
        events_list = []
        for event in result["events"]:
            events_list.append(EventList(
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
        
        return {
            "events": events_list,
            "total": result["total"],
            "page": result["page"],
            "limit": result["limit"],
            "pages": result["pages"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{event_id}", response_model=EventOut)
def get_event(
    event_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get event by ID"""
    try:
        event = event_service.get_event(db, event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")
        
        # Increment views count
        event_service.increment_views(db, event_id)
        
        return EventOut(
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
            gallery_urls=event.gallery_urls.split(',') if event.gallery_urls else None,
            organizer_name=event.organizer_name,
            organizer_email=event.organizer_email,
            organizer_phone=event.organizer_phone,
            is_featured=event.is_featured,
            allow_waitlist=event.allow_waitlist,
            require_approval=event.require_approval,
            organizer_id=event.organizer_id,
            is_active=event.is_active,
            views_count=event.views_count,
            likes_count=event.likes_count,
            shares_count=event.shares_count,
            created_at=event.created_at,
            updated_at=event.updated_at,
            published_at=event.published_at
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{event_id}", response_model=EventOut)
def update_event(
    event_id: int,
    event: EventUpdate,
    current_user: User = Depends(require_permission("event:update")),
    db: Session = Depends(get_db)
):
    """Update event"""
    try:
        updated_event = event_service.update_event(db, event_id, event, current_user.id)
        if not updated_event:
            raise HTTPException(status_code=404, detail="Event not found or access denied")
        
        return EventOut(
            id=updated_event.id,
            title=updated_event.title,
            description=updated_event.description,
            short_description=updated_event.short_description,
            category=updated_event.category,
            status=updated_event.status,
            start_date=updated_event.start_date,
            end_date=updated_event.end_date,
            start_time=updated_event.start_time,
            end_time=updated_event.end_time,
            location=updated_event.location,
            address=updated_event.address,
            city=updated_event.city,
            country=updated_event.country,
            is_online=updated_event.is_online,
            online_url=updated_event.online_url,
            max_capacity=updated_event.max_capacity,
            current_registrations=updated_event.current_registrations,
            price=updated_event.price,
            currency=updated_event.currency,
            is_free=updated_event.is_free,
            flyer_url=updated_event.flyer_url,
            banner_url=updated_event.banner_url,
            gallery_urls=updated_event.gallery_urls.split(',') if updated_event.gallery_urls else None,
            organizer_name=updated_event.organizer_name,
            organizer_email=updated_event.organizer_email,
            organizer_phone=updated_event.organizer_phone,
            is_featured=updated_event.is_featured,
            allow_waitlist=updated_event.allow_waitlist,
            require_approval=updated_event.require_approval,
            organizer_id=updated_event.organizer_id,
            is_active=updated_event.is_active,
            views_count=updated_event.views_count,
            likes_count=updated_event.likes_count,
            shares_count=updated_event.shares_count,
            created_at=updated_event.created_at,
            updated_at=updated_event.updated_at,
            published_at=updated_event.published_at
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{event_id}")
def delete_event(
    event_id: int,
    current_user: User = Depends(require_permission("event:delete")),
    db: Session = Depends(get_db)
):
    """Delete event"""
    try:
        success = event_service.delete_event(db, event_id, current_user.id)
        if not success:
            raise HTTPException(status_code=404, detail="Event not found or access denied")
        
        return {"message": "Event deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{event_id}/publish")
def publish_event(
    event_id: int,
    current_user: User = Depends(require_permission("event:update")),
    db: Session = Depends(get_db)
):
    """Publish event"""
    try:
        published_event = event_service.publish_event(db, event_id, current_user.id)
        if not published_event:
            raise HTTPException(status_code=404, detail="Event not found or access denied")
        
        return {"message": "Event published successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Event Interactions

@router.post("/{event_id}/like")
def like_event(
    event_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Like an event"""
    try:
        success = event_service.like_event(db, event_id, current_user.id)
        if not success:
            raise HTTPException(status_code=400, detail="Already liked or event not found")
        
        return {"message": "Event liked successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{event_id}/like")
def unlike_event(
    event_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Unlike an event"""
    try:
        success = event_service.unlike_event(db, event_id, current_user.id)
        if not success:
            raise HTTPException(status_code=400, detail="Not liked or event not found")
        
        return {"message": "Event unliked successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{event_id}/register")
def register_for_event(
    event_id: int,
    registration: EventRegistrationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Register for an event"""
    try:
        registration_data = registration.dict()
        new_registration = event_service.register_for_event(db, event_id, current_user.id, registration_data)
        if not new_registration:
            raise HTTPException(status_code=400, detail="Registration failed or event not available")
        
        return {"message": "Registration successful", "status": new_registration.status}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Analytics Endpoints

@router.get("/{event_id}/analytics", response_model=EventAnalytics)
def get_event_analytics(
    event_id: int,
    current_user: User = Depends(require_permission("event:read")),
    db: Session = Depends(get_db)
):
    """Get event analytics"""
    try:
        analytics = event_service.get_event_analytics(db, event_id)
        if not analytics:
            raise HTTPException(status_code=404, detail="Event not found")
        
        return EventAnalytics(**analytics)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/analytics/stats", response_model=EventStats)
def get_global_stats(
    current_user: User = Depends(require_permission("event:read")),
    db: Session = Depends(get_db)
):
    """Get global event statistics"""
    try:
        stats = event_service.get_global_stats(db, current_user.id)
        return EventStats(**stats)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Special Event Lists

@router.get("/featured/list", response_model=List[EventList])
def get_featured_events(
    limit: int = Query(10, ge=1, le=50, description="Number of events to return"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get featured events"""
    try:
        events = event_service.get_featured_events(db, limit)
        events_list = []
        for event in events:
            events_list.append(EventList(
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
        
        return events_list
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/upcoming/list", response_model=List[EventList])
def get_upcoming_events(
    limit: int = Query(10, ge=1, le=50, description="Number of events to return"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get upcoming events"""
    try:
        events = event_service.get_upcoming_events(db, limit)
        events_list = []
        for event in events:
            events_list.append(EventList(
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
        
        return events_list
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
