from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class NotificationTypeEnum(str, Enum):
    EVENT_REMINDER = "event_reminder"
    PAYMENT_SUCCESS = "payment_success"
    PAYMENT_FAILED = "payment_failed"
    EVENT_UPDATE = "event_update"
    EVENT_CANCELLED = "event_cancelled"
    CERTIFICATE_READY = "certificate_ready"
    SYSTEM_ANNOUNCEMENT = "system_announcement"
    REGISTRATION_CONFIRMED = "registration_confirmed"
    ATTENDANCE_REMINDER = "attendance_reminder"

class NotificationPriorityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class NotificationStatusEnum(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    READ = "read"
    FAILED = "failed"

# Notification Schemas
class NotificationBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1)
    notification_type: NotificationTypeEnum
    priority: NotificationPriorityEnum = NotificationPriorityEnum.MEDIUM
    event_id: Optional[int] = None
    payment_id: Optional[int] = None
    certificate_id: Optional[int] = None
    action_url: Optional[str] = None
    notification_metadata: Optional[Dict[str, Any]] = None

class NotificationCreate(NotificationBase):
    user_id: int

class NotificationUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    message: Optional[str] = Field(None, min_length=1)
    priority: Optional[NotificationPriorityEnum] = None
    action_url: Optional[str] = None
    notification_metadata: Optional[Dict[str, Any]] = None

class NotificationResponse(NotificationBase):
    id: str
    status: NotificationStatusEnum
    created_at: datetime
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Notification Template Schemas
class NotificationTemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    notification_type: NotificationTypeEnum
    title_template: str = Field(..., min_length=1)
    message_template: str = Field(..., min_length=1)
    email_subject_template: Optional[str] = None
    email_body_template: Optional[str] = None
    priority: NotificationPriorityEnum = NotificationPriorityEnum.MEDIUM
    send_email: bool = True
    send_push: bool = True
    send_sms: bool = False
    send_in_app: bool = True
    variables: Optional[List[str]] = None

class NotificationTemplateCreate(NotificationTemplateBase):
    pass

class NotificationTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    title_template: Optional[str] = Field(None, min_length=1)
    message_template: Optional[str] = Field(None, min_length=1)
    email_subject_template: Optional[str] = None
    email_body_template: Optional[str] = None
    priority: Optional[NotificationPriorityEnum] = None
    send_email: Optional[bool] = None
    send_push: Optional[bool] = None
    send_sms: Optional[bool] = None
    send_in_app: Optional[bool] = None
    variables: Optional[List[str]] = None
    is_active: Optional[bool] = None

class NotificationTemplateResponse(NotificationTemplateBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Notification Preference Schemas
class NotificationPreferenceBase(BaseModel):
    email_enabled: bool = True
    push_enabled: bool = True
    sms_enabled: bool = False
    in_app_enabled: bool = True
    event_reminders: bool = True
    payment_notifications: bool = True
    event_updates: bool = True
    system_announcements: bool = True
    certificate_notifications: bool = True
    daily_digest: bool = False
    weekly_digest: bool = False
    quiet_hours_start: Optional[str] = Field(None, pattern="^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    quiet_hours_end: Optional[str] = Field(None, pattern="^([01]?[0-9]|2[0-3]):[0-5][0-9]$")

class NotificationPreferenceCreate(NotificationPreferenceBase):
    user_id: int

class NotificationPreferenceUpdate(BaseModel):
    email_enabled: Optional[bool] = None
    push_enabled: Optional[bool] = None
    sms_enabled: Optional[bool] = None
    in_app_enabled: Optional[bool] = None
    event_reminders: Optional[bool] = None
    payment_notifications: Optional[bool] = None
    event_updates: Optional[bool] = None
    system_announcements: Optional[bool] = None
    certificate_notifications: Optional[bool] = None
    daily_digest: Optional[bool] = None
    weekly_digest: Optional[bool] = None
    quiet_hours_start: Optional[str] = Field(None, pattern="^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    quiet_hours_end: Optional[str] = Field(None, pattern="^([01]?[0-9]|2[0-3]):[0-5][0-9]$")

class NotificationPreferenceResponse(NotificationPreferenceBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Bulk Notification Schemas
class BulkNotificationCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1)
    notification_type: NotificationTypeEnum = NotificationTypeEnum.SYSTEM_ANNOUNCEMENT
    priority: NotificationPriorityEnum = NotificationPriorityEnum.MEDIUM
    user_ids: List[int] = Field(..., min_items=1)
    action_url: Optional[str] = None
    notification_metadata: Optional[Dict[str, Any]] = None

# Notification Analytics Schemas
class NotificationAnalytics(BaseModel):
    total_notifications: int
    sent_notifications: int
    read_notifications: int
    failed_notifications: int
    delivery_rate: float
    read_rate: float
    type_distribution: Dict[str, int]
    priority_distribution: Dict[str, int]
    delivery_channels: Dict[str, int]
    daily_volume: List[Dict[str, Any]]

# WebSocket Message Schemas
class WebSocketMessage(BaseModel):
    type: str
    data: Dict[str, Any]
    timestamp: datetime

class NotificationWebSocketMessage(BaseModel):
    id: str
    title: str
    message: str
    type: str
    priority: str
    action_url: Optional[str] = None
    created_at: datetime
