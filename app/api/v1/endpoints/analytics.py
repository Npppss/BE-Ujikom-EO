from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta

from app.core.dependencies import get_db, get_current_active_user, require_permission
from app.db.models.models import User
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])

analytics_service = AnalyticsService()

@router.get("/dashboard")
async def get_dashboard_analytics(
    current_user: User = Depends(require_permission("analytics:read")),
    db: Session = Depends(get_db)
):
    """Get comprehensive dashboard analytics"""
    try:
        # For admin, show all data. For organizers, show only their events
        user_id = None if current_user.role.name == "admin" else current_user.id
        
        analytics = analytics_service.get_dashboard_overview(db, user_id)
        return analytics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/events/{event_id}")
async def get_event_analytics(
    event_id: int,
    current_user: User = Depends(require_permission("analytics:read")),
    db: Session = Depends(get_db)
):
    """Get detailed analytics for a specific event"""
    try:
        analytics = analytics_service.get_event_analytics(db, event_id)
        if not analytics:
            raise HTTPException(status_code=404, detail="Event not found")
        
        return analytics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/revenue")
async def get_revenue_analytics(
    start_date: Optional[datetime] = Query(None, description="Start date for analytics"),
    end_date: Optional[datetime] = Query(None, description="End date for analytics"),
    current_user: User = Depends(require_permission("analytics:read")),
    db: Session = Depends(get_db)
):
    """Get revenue analytics"""
    try:
        # For admin, show all data. For users, show only their data
        user_id = None if current_user.role.name == "admin" else current_user.id
        
        analytics = analytics_service.get_revenue_analytics(db, user_id, start_date, end_date)
        return analytics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users")
async def get_user_analytics(
    current_user: User = Depends(require_permission("analytics:read")),
    db: Session = Depends(get_db)
):
    """Get user analytics"""
    try:
        # Only admin can see user analytics
        if current_user.role.name != "admin":
            raise HTTPException(status_code=403, detail="Access denied")
        
        analytics = analytics_service.get_user_analytics(db)
        return analytics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/categories")
async def get_category_analytics(
    current_user: User = Depends(require_permission("analytics:read")),
    db: Session = Depends(get_db)
):
    """Get event category analytics"""
    try:
        analytics = analytics_service.get_event_category_analytics(db)
        return analytics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/notifications")
async def get_notification_analytics(
    current_user: User = Depends(require_permission("analytics:read")),
    db: Session = Depends(get_db)
):
    """Get notification analytics"""
    try:
        # For admin, show all data. For users, show only their data
        user_id = None if current_user.role.name == "admin" else current_user.id
        
        analytics = analytics_service.get_notification_analytics(db, user_id)
        return analytics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
