from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from app.db.models import Event, EventRegistration, EventLike, EventComment, User, EventStatus, EventCategory
from app.schemas.event import EventCreate, EventUpdate, EventSearchParams
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
import json

class EventService:
    def __init__(self):
        pass
    
    def create_event(self, db: Session, event_data: EventCreate, organizer_id: int) -> Event:
        """Create a new event"""
        # Convert gallery_urls to JSON string if provided
        gallery_urls_json = None
        if event_data.gallery_urls:
            gallery_urls_json = json.dumps(event_data.gallery_urls)
        
        # Create event object
        event_dict = event_data.dict()
        if gallery_urls_json:
            event_dict['gallery_urls'] = gallery_urls_json
        
        event = Event(
            **event_dict,
            organizer_id=organizer_id,
            status=EventStatus.DRAFT
        )
        
        db.add(event)
        db.commit()
        db.refresh(event)
        return event
    
    def get_event(self, db: Session, event_id: int) -> Optional[Event]:
        """Get event by ID"""
        return db.query(Event).filter(Event.id == event_id).first()
    
    def get_events(self, db: Session, params: EventSearchParams) -> Dict[str, Any]:
        """Get events with filtering and pagination"""
        query = db.query(Event)
        
        # Apply filters
        if params.search:
            search_term = f"%{params.search}%"
            query = query.filter(
                or_(
                    Event.title.ilike(search_term),
                    Event.description.ilike(search_term),
                    Event.location.ilike(search_term)
                )
            )
        
        if params.category:
            query = query.filter(Event.category == params.category)
        
        if params.status:
            query = query.filter(Event.status == params.status)
        
        if params.city:
            query = query.filter(Event.city.ilike(f"%{params.city}%"))
        
        if params.is_online is not None:
            query = query.filter(Event.is_online == params.is_online)
        
        if params.is_free is not None:
            query = query.filter(Event.is_free == params.is_free)
        
        if params.start_date:
            query = query.filter(Event.start_date >= params.start_date)
        
        if params.end_date:
            query = query.filter(Event.end_date <= params.end_date)
        
        if params.organizer_id:
            query = query.filter(Event.organizer_id == params.organizer_id)
        
        # Apply sorting
        if params.sort_order.lower() == "desc":
            query = query.order_by(desc(getattr(Event, params.sort_by)))
        else:
            query = query.order_by(asc(getattr(Event, params.sort_by)))
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (params.page - 1) * params.limit
        events = query.offset(offset).limit(params.limit).all()
        
        return {
            "events": events,
            "total": total,
            "page": params.page,
            "limit": params.limit,
            "pages": (total + params.limit - 1) // params.limit
        }
    
    def update_event(self, db: Session, event_id: int, event_data: EventUpdate, user_id: int) -> Optional[Event]:
        """Update event"""
        event = db.query(Event).filter(
            Event.id == event_id,
            Event.organizer_id == user_id
        ).first()
        
        if not event:
            return None
        
        # Convert gallery_urls to JSON string if provided
        update_data = event_data.dict(exclude_unset=True)
        if 'gallery_urls' in update_data and update_data['gallery_urls']:
            update_data['gallery_urls'] = json.dumps(update_data['gallery_urls'])
        
        # Update fields
        for field, value in update_data.items():
            setattr(event, field, value)
        
        # Set published_at if status changes to published
        if update_data.get('status') == EventStatus.PUBLISHED and event.status != EventStatus.PUBLISHED:
            event.published_at = datetime.utcnow()
        
        db.commit()
        db.refresh(event)
        return event
    
    def delete_event(self, db: Session, event_id: int, user_id: int) -> bool:
        """Delete event"""
        event = db.query(Event).filter(
            Event.id == event_id,
            Event.organizer_id == user_id
        ).first()
        
        if not event:
            return False
        
        db.delete(event)
        db.commit()
        return True
    
    def publish_event(self, db: Session, event_id: int, user_id: int) -> Optional[Event]:
        """Publish event"""
        event = db.query(Event).filter(
            Event.id == event_id,
            Event.organizer_id == user_id
        ).first()
        
        if not event:
            return None
        
        event.status = EventStatus.PUBLISHED
        event.published_at = datetime.utcnow()
        
        db.commit()
        db.refresh(event)
        return event
    
    def increment_views(self, db: Session, event_id: int) -> bool:
        """Increment event views count"""
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            return False
        
        event.views_count += 1
        db.commit()
        return True
    
    def like_event(self, db: Session, event_id: int, user_id: int) -> bool:
        """Like an event"""
        # Check if already liked
        existing_like = db.query(EventLike).filter(
            EventLike.event_id == event_id,
            EventLike.user_id == user_id
        ).first()
        
        if existing_like:
            return False
        
        # Create like
        like = EventLike(event_id=event_id, user_id=user_id)
        db.add(like)
        
        # Increment likes count
        event = db.query(Event).filter(Event.id == event_id).first()
        if event:
            event.likes_count += 1
        
        db.commit()
        return True
    
    def unlike_event(self, db: Session, event_id: int, user_id: int) -> bool:
        """Unlike an event"""
        like = db.query(EventLike).filter(
            EventLike.event_id == event_id,
            EventLike.user_id == user_id
        ).first()
        
        if not like:
            return False
        
        db.delete(like)
        
        # Decrement likes count
        event = db.query(Event).filter(Event.id == event_id).first()
        if event and event.likes_count > 0:
            event.likes_count -= 1
        
        db.commit()
        return True
    
    def register_for_event(self, db: Session, event_id: int, user_id: int, registration_data: dict) -> Optional[EventRegistration]:
        """Register user for an event"""
        # Check if event exists and is published
        event = db.query(Event).filter(
            Event.id == event_id,
            Event.status == EventStatus.PUBLISHED
        ).first()
        
        if not event:
            return None
        
        # Check if already registered
        existing_registration = db.query(EventRegistration).filter(
            EventRegistration.event_id == event_id,
            EventRegistration.user_id == user_id
        ).first()
        
        if existing_registration:
            return None
        
        # Check capacity
        if event.max_capacity and event.current_registrations >= event.max_capacity:
            if not event.allow_waitlist:
                return None
            registration_data['status'] = 'waitlisted'
        
        # Create registration
        registration = EventRegistration(
            event_id=event_id,
            user_id=user_id,
            **registration_data
        )
        
        db.add(registration)
        
        # Update event registration count
        if registration.status == 'confirmed':
            event.current_registrations += 1
        
        db.commit()
        db.refresh(registration)
        return registration
    
    def get_event_analytics(self, db: Session, event_id: int) -> Dict[str, Any]:
        """Get comprehensive analytics for an event"""
        event = db.query(Event).filter(Event.id == event_id).first()
        if not event:
            return None
        
        # Get registration stats
        registrations = db.query(EventRegistration).filter(EventRegistration.event_id == event_id).all()
        total_registrations = len(registrations)
        confirmed_registrations = len([r for r in registrations if r.status == 'confirmed'])
        waitlisted_registrations = len([r for r in registrations if r.status == 'waitlisted'])
        
        # Get attendance stats
        attendances = db.query(Event).filter(Event.id == event_id).first().attendances
        total_attendances = len([a for a in attendances if a.check_in_qr_scanned])
        
        # Get rating stats
        comments = db.query(EventComment).filter(
            EventComment.event_id == event_id,
            EventComment.rating.isnot(None)
        ).all()
        
        average_rating = None
        if comments:
            total_rating = sum(c.rating for c in comments)
            average_rating = total_rating / len(comments)
        
        # Calculate rates
        registration_rate = 0
        if event.max_capacity:
            registration_rate = (confirmed_registrations / event.max_capacity) * 100
        
        attendance_rate = 0
        if confirmed_registrations:
            attendance_rate = (total_attendances / confirmed_registrations) * 100
        
        # Calculate revenue
        revenue = sum(r.price_paid for r in registrations if r.price_paid and r.payment_status == 'paid')
        
        return {
            "event_id": event_id,
            "event_title": event.title,
            "total_views": event.views_count,
            "total_likes": event.likes_count,
            "total_shares": event.shares_count,
            "total_registrations": total_registrations,
            "confirmed_registrations": confirmed_registrations,
            "waitlisted_registrations": waitlisted_registrations,
            "total_attendances": total_attendances,
            "registration_rate": round(registration_rate, 2),
            "attendance_rate": round(attendance_rate, 2),
            "average_rating": round(average_rating, 2) if average_rating else None,
            "total_comments": len(comments),
            "revenue": revenue,
            "created_at": event.created_at
        }
    
    def get_global_stats(self, db: Session, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Get global event statistics"""
        query = db.query(Event)
        if user_id:
            query = query.filter(Event.organizer_id == user_id)
        
        events = query.all()
        
        # Basic stats
        total_events = len(events)
        published_events = len([e for e in events if e.status == EventStatus.PUBLISHED])
        ongoing_events = len([e for e in events if e.status == EventStatus.ONGOING])
        completed_events = len([e for e in events if e.status == EventStatus.COMPLETED])
        
        # Registration stats
        total_registrations = sum(e.current_registrations for e in events)
        
        # Revenue stats
        total_revenue = sum(e.price * e.current_registrations for e in events if not e.is_free)
        
        # Rating stats
        all_comments = db.query(EventComment).filter(EventComment.rating.isnot(None))
        if user_id:
            all_comments = all_comments.join(Event).filter(Event.organizer_id == user_id)
        
        comments = all_comments.all()
        average_rating = None
        if comments:
            total_rating = sum(c.rating for c in comments)
            average_rating = total_rating / len(comments)
        
        # Category stats
        category_counts = {}
        for event in events:
            category = event.category.value
            category_counts[category] = category_counts.get(category, 0) + 1
        
        top_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Monthly stats (last 12 months)
        monthly_stats = []
        for i in range(12):
            month_date = datetime.utcnow() - timedelta(days=30*i)
            month_events = [e for e in events if e.created_at.month == month_date.month and e.created_at.year == month_date.year]
            monthly_stats.append({
                "month": month_date.strftime("%Y-%m"),
                "events": len(month_events),
                "registrations": sum(e.current_registrations for e in month_events)
            })
        
        return {
            "total_events": total_events,
            "published_events": published_events,
            "ongoing_events": ongoing_events,
            "completed_events": completed_events,
            "total_registrations": total_registrations,
            "total_revenue": total_revenue,
            "average_rating": round(average_rating, 2) if average_rating else None,
            "top_categories": [{"category": cat, "count": count} for cat, count in top_categories],
            "monthly_stats": monthly_stats
        }
    
    def get_featured_events(self, db: Session, limit: int = 10) -> List[Event]:
        """Get featured events"""
        return db.query(Event).filter(
            Event.is_featured == True,
            Event.status == EventStatus.PUBLISHED,
            Event.is_active == True
        ).order_by(desc(Event.views_count)).limit(limit).all()
    
    def get_upcoming_events(self, db: Session, limit: int = 10) -> List[Event]:
        """Get upcoming events"""
        today = date.today()
        return db.query(Event).filter(
            Event.start_date >= today,
            Event.status == EventStatus.PUBLISHED,
            Event.is_active == True
        ).order_by(Event.start_date).limit(limit).all()

# Create service instance
event_service = EventService() 