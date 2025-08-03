from sqlalchemy import Column, Integer, String, Date, Time, DateTime, Boolean, ForeignKey, Text, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import uuid
import enum

def generate_uuid():
    return str(uuid.uuid4())

class EventStatus(enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class EventCategory(enum.Enum):
    BUSINESS = "business"
    ENTERTAINMENT = "entertainment"
    EDUCATION = "education"
    TECHNOLOGY = "technology"
    HEALTH = "health"
    SPORTS = "sports"
    CULTURE = "culture"
    OTHER = "other"

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    short_description = Column(String(500), nullable=True)
    
    # Event Details
    category = Column(Enum(EventCategory), default=EventCategory.OTHER)
    status = Column(Enum(EventStatus), default=EventStatus.DRAFT)
    
    # Date & Time
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    
    # Location
    location = Column(String(255), nullable=False)
    address = Column(Text, nullable=True)
    city = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    is_online = Column(Boolean, default=False)
    online_url = Column(String(500), nullable=True)
    
    # Capacity & Pricing
    max_capacity = Column(Integer, nullable=True)
    current_registrations = Column(Integer, default=0)
    price = Column(Float, default=0.0)
    currency = Column(String(3), default="IDR")
    is_free = Column(Boolean, default=True)
    
    # Media
    flyer_url = Column(String(500), nullable=True)
    banner_url = Column(String(500), nullable=True)
    gallery_urls = Column(Text, nullable=True)  # JSON array of URLs
    
    # Organizer Info
    organizer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    organizer_name = Column(String(255), nullable=True)
    organizer_email = Column(String(255), nullable=True)
    organizer_phone = Column(String(20), nullable=True)
    
    # Event Settings
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    allow_waitlist = Column(Boolean, default=True)
    require_approval = Column(Boolean, default=False)
    
    # Attendance tracking fields
    check_in_started = Column(Boolean, default=False)
    check_out_started = Column(Boolean, default=False)
    check_in_qr_code = Column(String(500), unique=True, default=generate_uuid)
    check_out_qr_code = Column(String(500), unique=True, default=generate_uuid)
    
    # Analytics fields
    views_count = Column(Integer, default=0)
    likes_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    organizer = relationship("User", back_populates="organized_events")
    attendances = relationship("Attendance", back_populates="event", cascade="all, delete-orphan")
    registrations = relationship("EventRegistration", back_populates="event", cascade="all, delete-orphan")
    likes = relationship("EventLike", back_populates="event", cascade="all, delete-orphan")
    comments = relationship("EventComment", back_populates="event", cascade="all, delete-orphan")
    certificates = relationship("Certificate", back_populates="event", cascade="all, delete-orphan")

class EventRegistration(Base):
    __tablename__ = "event_registrations"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Registration details
    registration_date = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(20), default="confirmed")  # confirmed, cancelled, waitlisted
    ticket_type = Column(String(50), nullable=True)  # early_bird, regular, vip
    price_paid = Column(Float, nullable=True)
    payment_status = Column(String(20), default="pending")  # pending, paid, failed
    
    # Additional info
    special_requirements = Column(Text, nullable=True)
    dietary_restrictions = Column(String(255), nullable=True)
    emergency_contact = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    event = relationship("Event", back_populates="registrations")
    user = relationship("User", back_populates="event_registrations")

class EventLike(Base):
    __tablename__ = "event_likes"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    event = relationship("Event", back_populates="likes")
    user = relationship("User", back_populates="event_likes")

class EventComment(Base):
    __tablename__ = "event_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Comment details
    content = Column(Text, nullable=False)
    rating = Column(Integer, nullable=True)  # 1-5 stars
    is_approved = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    event = relationship("Event", back_populates="comments")
    user = relationship("User", back_populates="event_comments")

class Attendance(Base):
    __tablename__ = "attendances"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Attendance status
    check_in_time = Column(DateTime(timezone=True), nullable=True)
    check_out_time = Column(DateTime(timezone=True), nullable=True)
    check_in_qr_scanned = Column(Boolean, default=False)
    check_out_qr_scanned = Column(Boolean, default=False)
    
    # Additional info
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    event = relationship("Event", back_populates="attendances")
    user = relationship("User", back_populates="attendances")
