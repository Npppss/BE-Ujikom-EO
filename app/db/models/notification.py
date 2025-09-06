from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import uuid
import enum

def generate_notification_id():
    return f"NOTIF-{str(uuid.uuid4())[:8].upper()}"

class NotificationType(enum.Enum):
    EVENT_REMINDER = "event_reminder"
    PAYMENT_SUCCESS = "payment_success"
    PAYMENT_FAILED = "payment_failed"
    EVENT_UPDATE = "event_update"
    EVENT_CANCELLED = "event_cancelled"
    CERTIFICATE_READY = "certificate_ready"
    SYSTEM_ANNOUNCEMENT = "system_announcement"
    REGISTRATION_CONFIRMED = "registration_confirmed"
    ATTENDANCE_REMINDER = "attendance_reminder"

class NotificationPriority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class NotificationStatus(enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    READ = "read"
    FAILED = "failed"

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(String(50), unique=True, index=True, default=generate_notification_id)
    
    # Notification details
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(Enum(NotificationType), nullable=False)
    priority = Column(Enum(NotificationPriority), default=NotificationPriority.MEDIUM)
    status = Column(Enum(NotificationStatus), default=NotificationStatus.PENDING)
    
    # Recipient
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Related entities
    event_id = Column(Integer, ForeignKey("events.id"), nullable=True)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=True)
    certificate_id = Column(Integer, ForeignKey("certificates.id"), nullable=True)
    
    # Delivery channels
    send_email = Column(Boolean, default=True)
    send_push = Column(Boolean, default=True)
    send_sms = Column(Boolean, default=False)
    send_in_app = Column(Boolean, default=True)
    
    # Delivery status
    email_sent = Column(Boolean, default=False)
    push_sent = Column(Boolean, default=False)
    sms_sent = Column(Boolean, default=False)
    in_app_sent = Column(Boolean, default=False)
    
    # Metadata
    notification_metadata = Column(Text, nullable=True)  # JSON string for additional data
    action_url = Column(String(500), nullable=True)  # URL for action button
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    event = relationship("Event", back_populates="notifications")
    payment = relationship("Payment", back_populates="notifications")
    certificate = relationship("Certificate", back_populates="notifications")
    logs = relationship("NotificationLog", back_populates="notification", cascade="all, delete-orphan")

class NotificationTemplate(Base):
    __tablename__ = "notification_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    notification_type = Column(Enum(NotificationType), nullable=False)
    
    # Template content
    title_template = Column(Text, nullable=False)
    message_template = Column(Text, nullable=False)
    email_subject_template = Column(Text, nullable=True)
    email_body_template = Column(Text, nullable=True)
    
    # Template settings
    priority = Column(Enum(NotificationPriority), default=NotificationPriority.MEDIUM)
    send_email = Column(Boolean, default=True)
    send_push = Column(Boolean, default=True)
    send_sms = Column(Boolean, default=False)
    send_in_app = Column(Boolean, default=True)
    
    # Template variables
    variables = Column(Text, nullable=True)  # JSON array of available variables
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

class NotificationPreference(Base):
    __tablename__ = "notification_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Channel preferences
    email_enabled = Column(Boolean, default=True)
    push_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=False)
    in_app_enabled = Column(Boolean, default=True)
    
    # Type preferences
    event_reminders = Column(Boolean, default=True)
    payment_notifications = Column(Boolean, default=True)
    event_updates = Column(Boolean, default=True)
    system_announcements = Column(Boolean, default=True)
    certificate_notifications = Column(Boolean, default=True)
    
    # Frequency preferences
    daily_digest = Column(Boolean, default=False)
    weekly_digest = Column(Boolean, default=False)
    quiet_hours_start = Column(String(5), nullable=True)  # HH:MM format
    quiet_hours_end = Column(String(5), nullable=True)    # HH:MM format
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="notification_preferences")

class NotificationLog(Base):
    __tablename__ = "notification_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(Integer, ForeignKey("notifications.id"), nullable=False)
    
    # Delivery details
    channel = Column(String(20), nullable=False)  # email, push, sms, in_app
    status = Column(String(20), nullable=False)   # success, failed, pending
    error_message = Column(Text, nullable=True)
    
    # Delivery metadata
    provider = Column(String(50), nullable=True)  # smtp, firebase, twilio, etc.
    provider_message_id = Column(String(255), nullable=True)
    delivery_time = Column(Integer, nullable=True)  # milliseconds
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    notification = relationship("Notification", back_populates="logs")
