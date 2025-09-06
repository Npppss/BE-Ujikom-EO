from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import uuid
import enum

def generate_payment_id():
    return f"PAY-{str(uuid.uuid4())[:8].upper()}"

def generate_ticket_id():
    return f"TIX-{str(uuid.uuid4())[:8].upper()}"

class PaymentStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class PaymentMethod(enum.Enum):
    CREDIT_CARD = "credit_card"
    BANK_TRANSFER = "bank_transfer"
    E_WALLET = "e_wallet"
    CASH = "cash"
    QRIS = "qris"

class TicketType(enum.Enum):
    EARLY_BIRD = "early_bird"
    REGULAR = "regular"
    VIP = "vip"
    STUDENT = "student"
    CORPORATE = "corporate"

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(String(50), unique=True, index=True, default=generate_payment_id)

    # Payment details
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="IDR")
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)

    # External payment provider
    provider = Column(String(50), nullable=False)  # stripe, midtrans, xendit
    provider_payment_id = Column(String(255), nullable=True)
    provider_fee = Column(Float, default=0.0)

    # Relationships
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    registration_id = Column(Integer, ForeignKey("event_registrations.id"), nullable=False)

    # Payment metadata
    description = Column(Text, nullable=True)
    payment_metadata = Column(Text, nullable=True)  # JSON string for additional data

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    paid_at = Column(DateTime(timezone=True), nullable=True)
    expired_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="payments")
    event = relationship("Event", back_populates="payments")
    registration = relationship("EventRegistration", back_populates="payment")
    refunds = relationship("Refund", back_populates="payment", cascade="all, delete-orphan")
    discount_usages = relationship("DiscountCodeUsage", back_populates="payment", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="payment", cascade="all, delete-orphan")

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(String(50), unique=True, index=True, default=generate_ticket_id)

    # Ticket details
    ticket_type = Column(Enum(TicketType), nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String(3), default="IDR")
    quantity_available = Column(Integer, nullable=False)
    quantity_sold = Column(Integer, default=0)

    # Ticket features
    features = Column(Text, nullable=True)  # JSON array of features
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)

    # Sale period
    sale_start_date = Column(DateTime(timezone=True), nullable=True)
    sale_end_date = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    event = relationship("Event", back_populates="tickets")

class DiscountCode(Base):
    __tablename__ = "discount_codes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)

    # Discount details
    discount_type = Column(String(20), nullable=False)  # percentage, fixed
    discount_value = Column(Float, nullable=False)
    minimum_amount = Column(Float, default=0.0)
    maximum_discount = Column(Float, nullable=True)

    # Usage limits
    max_usage = Column(Integer, nullable=True)
    current_usage = Column(Integer, default=0)
    max_usage_per_user = Column(Integer, default=1)

    # Validity period
    valid_from = Column(DateTime(timezone=True), nullable=True)
    valid_until = Column(DateTime(timezone=True), nullable=True)

    # Applicability
    applicable_events = Column(Text, nullable=True)  # JSON array of event IDs
    applicable_ticket_types = Column(Text, nullable=True)  # JSON array of ticket types

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    usages = relationship("DiscountCodeUsage", back_populates="discount_code", cascade="all, delete-orphan")

class DiscountCodeUsage(Base):
    __tablename__ = "discount_code_usages"

    id = Column(Integer, primary_key=True, index=True)
    discount_code_id = Column(Integer, ForeignKey("discount_codes.id"), nullable=False)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Usage details
    discount_amount = Column(Float, nullable=False)
    original_amount = Column(Float, nullable=False)
    final_amount = Column(Float, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    discount_code = relationship("DiscountCode", back_populates="usages")
    payment = relationship("Payment", back_populates="discount_usages")
    user = relationship("User")

class Refund(Base):
    __tablename__ = "refunds"

    id = Column(Integer, primary_key=True, index=True)
    refund_id = Column(String(50), unique=True, index=True, default=lambda: f"REF-{str(uuid.uuid4())[:8].upper()}")
    
    # Refund details
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=False)
    amount = Column(Float, nullable=False)
    reason = Column(Text, nullable=False)
    refund_status = Column(String(20), default="pending")  # pending, processed, failed
    
    # Refund metadata
    processed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    payment = relationship("Payment", back_populates="refunds")
    processor = relationship("User")
