from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class PaymentMethodEnum(str, Enum):
    CREDIT_CARD = "credit_card"
    BANK_TRANSFER = "bank_transfer"
    E_WALLET = "e_wallet"
    CASH = "cash"
    QRIS = "qris"

class PaymentStatusEnum(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class TicketTypeEnum(str, Enum):
    EARLY_BIRD = "early_bird"
    REGULAR = "regular"
    VIP = "vip"
    STUDENT = "student"
    CORPORATE = "corporate"

# Payment Schemas
class PaymentBase(BaseModel):
    amount: float = Field(..., gt=0, description="Payment amount")
    currency: str = Field(default="IDR", max_length=3)
    payment_method: PaymentMethodEnum
    description: Optional[str] = None

class PaymentCreate(PaymentBase):
    event_id: int
    ticket_type: TicketTypeEnum
    discount_code: Optional[str] = None

class PaymentUpdate(BaseModel):
    payment_status: Optional[PaymentStatusEnum] = None
    provider_payment_id: Optional[str] = None
    provider_fee: Optional[float] = None
    payment_metadata: Optional[Dict[str, Any]] = None

class PaymentResponse(PaymentBase):
    id: int
    payment_id: str
    payment_status: PaymentStatusEnum
    provider: str
    provider_payment_id: Optional[str]
    provider_fee: float
    user_id: int
    event_id: int
    registration_id: int
    payment_metadata: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    paid_at: Optional[datetime]
    expired_at: Optional[datetime]

    class Config:
        from_attributes = True

# Ticket Schemas
class TicketBase(BaseModel):
    ticket_type: TicketTypeEnum
    price: float = Field(..., ge=0)
    currency: str = Field(default="IDR", max_length=3)
    quantity_available: int = Field(..., gt=0)
    features: Optional[List[str]] = None
    description: Optional[str] = None
    sale_start_date: Optional[datetime] = None
    sale_end_date: Optional[datetime] = None

class TicketCreate(TicketBase):
    event_id: int

class TicketUpdate(BaseModel):
    price: Optional[float] = Field(None, ge=0)
    quantity_available: Optional[int] = Field(None, gt=0)
    features: Optional[List[str]] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    sale_start_date: Optional[datetime] = None
    sale_end_date: Optional[datetime] = None

class TicketResponse(TicketBase):
    id: int
    ticket_id: str
    quantity_sold: int
    is_active: bool
    event_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Discount Code Schemas
class DiscountCodeBase(BaseModel):
    code: str = Field(..., min_length=3, max_length=50)
    discount_type: str = Field(..., pattern="^(percentage|fixed)$")
    discount_value: float = Field(..., gt=0)
    minimum_amount: float = Field(default=0.0, ge=0)
    maximum_discount: Optional[float] = Field(None, gt=0)
    max_usage: Optional[int] = Field(None, gt=0)
    max_usage_per_user: int = Field(default=1, gt=0)
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    applicable_events: Optional[List[int]] = None
    applicable_ticket_types: Optional[List[str]] = None

class DiscountCodeCreate(DiscountCodeBase):
    pass

class DiscountCodeUpdate(BaseModel):
    discount_value: Optional[float] = Field(None, gt=0)
    minimum_amount: Optional[float] = Field(None, ge=0)
    maximum_discount: Optional[float] = Field(None, gt=0)
    max_usage: Optional[int] = Field(None, gt=0)
    max_usage_per_user: Optional[int] = Field(None, gt=0)
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    applicable_events: Optional[List[int]] = None
    applicable_ticket_types: Optional[List[str]] = None
    is_active: Optional[bool] = None

class DiscountCodeResponse(DiscountCodeBase):
    id: int
    current_usage: int
    is_active: bool
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Refund Schemas
class RefundBase(BaseModel):
    amount: float = Field(..., gt=0)
    reason: str = Field(..., min_length=10)
    notes: Optional[str] = None

class RefundCreate(RefundBase):
    payment_id: int

class RefundUpdate(BaseModel):
    refund_status: Optional[str] = Field(None, pattern="^(pending|processed|failed)$")
    notes: Optional[str] = None

class RefundResponse(RefundBase):
    id: int
    refund_id: str
    payment_id: int
    refund_status: str
    processed_by: Optional[int]
    created_at: datetime
    processed_at: Optional[datetime]

    class Config:
        from_attributes = True

# Payment Processing Schemas
class PaymentIntentCreate(BaseModel):
    event_id: int
    ticket_type: TicketTypeEnum
    quantity: int = Field(1, ge=1, le=10)
    discount_code: Optional[str] = None
    payment_method: PaymentMethodEnum

class PaymentIntentResponse(BaseModel):
    payment_intent_id: str
    client_secret: str
    amount: float
    currency: str
    payment_method: PaymentMethodEnum
    expires_at: datetime

# Analytics Schemas
class PaymentAnalytics(BaseModel):
    total_payments: int
    total_revenue: float
    successful_payments: int
    failed_payments: int
    pending_payments: int
    average_payment_amount: float
    payment_methods_distribution: Dict[str, int]
    monthly_revenue: List[Dict[str, Any]]

class TicketAnalytics(BaseModel):
    total_tickets_sold: int
    total_revenue: float
    tickets_by_type: Dict[str, int]
    average_ticket_price: float
    best_selling_ticket: str
    revenue_by_ticket_type: Dict[str, float]
