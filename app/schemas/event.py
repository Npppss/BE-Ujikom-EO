from pydantic import BaseModel, Field
from datetime import date, time, datetime
from typing import Optional, List
from enum import Enum

class EventStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class EventCategory(str, Enum):
    BUSINESS = "business"
    ENTERTAINMENT = "entertainment"
    EDUCATION = "education"
    TECHNOLOGY = "technology"
    HEALTH = "health"
    SPORTS = "sports"
    CULTURE = "culture"
    OTHER = "other"

# Event Schemas
class EventBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)
    category: EventCategory = EventCategory.OTHER
    start_date: date
    end_date: date
    start_time: time
    end_time: time
    location: str = Field(..., min_length=1, max_length=255)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    is_online: bool = False
    online_url: Optional[str] = None
    max_capacity: Optional[int] = Field(None, ge=1)
    price: float = Field(0.0, ge=0)
    currency: str = Field("IDR", max_length=3)
    is_free: bool = True
    flyer_url: Optional[str] = None
    banner_url: Optional[str] = None
    gallery_urls: Optional[List[str]] = None
    organizer_name: Optional[str] = Field(None, max_length=255)
    organizer_email: Optional[str] = None
    organizer_phone: Optional[str] = Field(None, max_length=20)
    is_featured: bool = False
    allow_waitlist: bool = True
    require_approval: bool = False

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)
    category: Optional[EventCategory] = None
    status: Optional[EventStatus] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    location: Optional[str] = Field(None, min_length=1, max_length=255)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    is_online: Optional[bool] = None
    online_url: Optional[str] = None
    max_capacity: Optional[int] = Field(None, ge=1)
    price: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = Field(None, max_length=3)
    is_free: Optional[bool] = None
    flyer_url: Optional[str] = None
    banner_url: Optional[str] = None
    gallery_urls: Optional[List[str]] = None
    organizer_name: Optional[str] = Field(None, max_length=255)
    organizer_email: Optional[str] = None
    organizer_phone: Optional[str] = Field(None, max_length=20)
    is_featured: Optional[bool] = None
    allow_waitlist: Optional[bool] = None
    require_approval: Optional[bool] = None

class EventOut(EventBase):
    id: int
    status: EventStatus
    organizer_id: int
    current_registrations: int
    is_active: bool
    views_count: int
    likes_count: int
    shares_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class EventList(BaseModel):
    id: int
    title: str
    short_description: Optional[str]
    category: EventCategory
    status: EventStatus
    start_date: date
    start_time: time
    location: str
    city: Optional[str]
    is_online: bool
    price: float
    is_free: bool
    flyer_url: Optional[str]
    organizer_name: Optional[str]
    current_registrations: int
    max_capacity: Optional[int]
    views_count: int
    likes_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Registration Schemas
class EventRegistrationCreate(BaseModel):
    event_id: int
    ticket_type: Optional[str] = Field(None, max_length=50)
    special_requirements: Optional[str] = None
    dietary_restrictions: Optional[str] = Field(None, max_length=255)
    emergency_contact: Optional[str] = Field(None, max_length=255)

class EventRegistrationUpdate(BaseModel):
    status: Optional[str] = Field(None, max_length=20)
    ticket_type: Optional[str] = Field(None, max_length=50)
    special_requirements: Optional[str] = None
    dietary_restrictions: Optional[str] = Field(None, max_length=255)
    emergency_contact: Optional[str] = Field(None, max_length=255)

class EventRegistrationOut(BaseModel):
    id: int
    event_id: int
    user_id: int
    user_name: str
    user_email: str
    registration_date: datetime
    status: str
    ticket_type: Optional[str]
    price_paid: Optional[float]
    payment_status: str
    special_requirements: Optional[str]
    dietary_restrictions: Optional[str]
    emergency_contact: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Like & Comment Schemas
class EventLikeCreate(BaseModel):
    event_id: int

class EventLikeOut(BaseModel):
    id: int
    event_id: int
    user_id: int
    user_name: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class EventCommentCreate(BaseModel):
    event_id: int
    content: str = Field(..., min_length=1)
    rating: Optional[int] = Field(None, ge=1, le=5)

class EventCommentUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1)
    rating: Optional[int] = Field(None, ge=1, le=5)

class EventCommentOut(BaseModel):
    id: int
    event_id: int
    user_id: int
    user_name: str
    content: str
    rating: Optional[int]
    is_approved: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Analytics Schemas
class EventAnalytics(BaseModel):
    event_id: int
    event_title: str
    total_views: int
    total_likes: int
    total_shares: int
    total_registrations: int
    total_attendances: int
    registration_rate: float  # percentage
    attendance_rate: float  # percentage
    average_rating: Optional[float]
    total_comments: int
    revenue: Optional[float]
    created_at: datetime

class EventSearchParams(BaseModel):
    search: Optional[str] = None
    category: Optional[EventCategory] = None
    status: Optional[EventStatus] = None
    city: Optional[str] = None
    is_online: Optional[bool] = None
    is_free: Optional[bool] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    organizer_id: Optional[int] = None
    page: int = Field(1, ge=1)
    limit: int = Field(10, ge=1, le=100)
    sort_by: str = "created_at"
    sort_order: str = "desc"

class EventStats(BaseModel):
    total_events: int
    published_events: int
    ongoing_events: int
    completed_events: int
    total_registrations: int
    total_revenue: float
    average_rating: Optional[float]
    top_categories: List[dict]
    monthly_stats: List[dict]
