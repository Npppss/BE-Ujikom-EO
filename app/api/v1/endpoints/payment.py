from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import json
import logging

from app.core.dependencies import get_db, get_current_active_user, require_permission
from app.db.models.models import User
from app.db.models.payment import Payment, Ticket, Refund
from app.schemas.payment import (
    PaymentCreate, PaymentResponse, PaymentUpdate, TicketCreate, TicketResponse,
    DiscountCodeCreate, DiscountCodeResponse, RefundCreate, RefundResponse,
    PaymentIntentCreate, PaymentIntentResponse, PaymentAnalytics, TicketAnalytics
)
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/payments", tags=["Payments"])

payment_service = PaymentService()

@router.post("/create-intent", response_model=PaymentIntentResponse)
async def create_payment_intent(
    payment_data: PaymentIntentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create payment intent for Stripe"""
    try:
        result = payment_service.create_payment_intent(
            db, payment_data.dict(), current_user.id
        )
        return PaymentIntentResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle Stripe webhook events"""
    try:
        # Get the raw body
        body = await request.body()
        
        # Verify webhook signature (implement proper verification)
        # For now, just process the event
        
        import json
        event_data = json.loads(body)
        
        success = payment_service.process_payment_webhook(db, event_data)
        
        if success:
            return {"status": "success"}
        else:
            raise HTTPException(status_code=400, detail="Webhook processing failed")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[PaymentResponse])
async def get_payments(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=50, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by payment status"),
    current_user: User = Depends(require_permission("payment:read")),
    db: Session = Depends(get_db)
):
    """Get payments with pagination and filters"""
    try:
        offset = (page - 1) * limit
        
        # Build query
        query = db.query(Payment)
        
        # Filter by user if not admin
        if current_user.role.name != "admin":
            query = query.filter(Payment.user_id == current_user.id)
        
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

@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get payment by ID"""
    try:
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        # Check access permission
        if current_user.role.name != "admin" and payment.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return PaymentResponse(
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
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/overview", response_model=PaymentAnalytics)
async def get_payment_analytics(
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    current_user: User = Depends(require_permission("analytics:read")),
    db: Session = Depends(get_db)
):
    """Get payment analytics"""
    try:
        # For admin, show all data. For users, show only their data
        user_id = None if current_user.role.name == "admin" else current_user.id
        
        analytics = payment_service.get_payment_analytics(db, user_id, start_date, end_date)
        return PaymentAnalytics(**analytics)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Ticket Management Endpoints
@router.post("/tickets", response_model=TicketResponse)
async def create_ticket(
    ticket_data: TicketCreate,
    current_user: User = Depends(require_permission("ticket:create")),
    db: Session = Depends(get_db)
):
    """Create new ticket type for event"""
    try:
        ticket = payment_service.create_ticket(db, ticket_data)
        return TicketResponse(
            id=ticket.id,
            ticket_id=ticket.ticket_id,
            ticket_type=ticket.ticket_type.value,
            price=ticket.price,
            currency=ticket.currency,
            quantity_available=ticket.quantity_available,
            quantity_sold=ticket.quantity_sold,
            features=json.loads(ticket.features) if ticket.features else None,
            description=ticket.description,
            is_active=ticket.is_active,
            sale_start_date=ticket.sale_start_date,
            sale_end_date=ticket.sale_end_date,
            event_id=ticket.event_id,
            created_at=ticket.created_at,
            updated_at=ticket.updated_at
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/tickets/event/{event_id}", response_model=List[TicketResponse])
async def get_event_tickets(
    event_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get tickets for a specific event"""
    try:
        tickets = db.query(Ticket).filter(
            Ticket.event_id == event_id,
            Ticket.is_active == True
        ).all()
        
        ticket_list = []
        for ticket in tickets:
            ticket_list.append(TicketResponse(
                id=ticket.id,
                ticket_id=ticket.ticket_id,
                ticket_type=ticket.ticket_type.value,
                price=ticket.price,
                currency=ticket.currency,
                quantity_available=ticket.quantity_available,
                quantity_sold=ticket.quantity_sold,
                features=json.loads(ticket.features) if ticket.features else None,
                description=ticket.description,
                is_active=ticket.is_active,
                sale_start_date=ticket.sale_start_date,
                sale_end_date=ticket.sale_end_date,
                event_id=ticket.event_id,
                created_at=ticket.created_at,
                updated_at=ticket.updated_at
            ))
        
        return ticket_list
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Discount Code Management Endpoints
@router.post("/discount-codes", response_model=DiscountCodeResponse)
async def create_discount_code(
    discount_data: DiscountCodeCreate,
    current_user: User = Depends(require_permission("discount:create")),
    db: Session = Depends(get_db)
):
    """Create new discount code"""
    try:
        discount = payment_service.create_discount_code(db, discount_data, current_user.id)
        return DiscountCodeResponse(
            id=discount.id,
            code=discount.code,
            discount_type=discount.discount_type,
            discount_value=discount.discount_value,
            minimum_amount=discount.minimum_amount,
            maximum_discount=discount.maximum_discount,
            max_usage=discount.max_usage,
            current_usage=discount.current_usage,
            max_usage_per_user=discount.max_usage_per_user,
            valid_from=discount.valid_from,
            valid_until=discount.valid_until,
            applicable_events=json.loads(discount.applicable_events) if discount.applicable_events else None,
            applicable_ticket_types=json.loads(discount.applicable_ticket_types) if discount.applicable_ticket_types else None,
            is_active=discount.is_active,
            created_by=discount.created_by,
            created_at=discount.created_at,
            updated_at=discount.updated_at
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/discount-codes/validate/{code}")
async def validate_discount_code(
    code: str,
    event_id: int = Query(..., description="Event ID"),
    ticket_type: str = Query(..., description="Ticket type"),
    amount: float = Query(..., description="Amount to validate"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Validate discount code"""
    try:
        discount_amount = payment_service._calculate_discount(
            db, code, amount, event_id, ticket_type
        )
        
        return {
            "valid": discount_amount > 0,
            "discount_amount": discount_amount,
            "final_amount": amount - discount_amount
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Refund Management Endpoints
@router.post("/refunds", response_model=RefundResponse)
async def create_refund(
    refund_data: RefundCreate,
    current_user: User = Depends(require_permission("refund:create")),
    db: Session = Depends(get_db)
):
    """Create refund request"""
    try:
        refund = payment_service.create_refund(db, refund_data, current_user.id)
        return RefundResponse(
            id=refund.id,
            refund_id=refund.refund_id,
            payment_id=refund.payment_id,
            amount=refund.amount,
            reason=refund.reason,
            notes=refund.notes,
            refund_status=refund.refund_status,
            processed_by=refund.processed_by,
            created_at=refund.created_at,
            processed_at=refund.processed_at
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/refunds", response_model=List[RefundResponse])
async def get_refunds(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=50, description="Items per page"),
    current_user: User = Depends(require_permission("refund:read")),
    db: Session = Depends(get_db)
):
    """Get refunds with pagination"""
    try:
        offset = (page - 1) * limit
        
        # Build query
        query = db.query(Refund)
        
        # Filter by user if not admin
        if current_user.role.name != "admin":
            query = query.filter(Refund.processed_by == current_user.id)
        
        # Get paginated results
        refunds = query.order_by(Refund.created_at.desc()).offset(offset).limit(limit).all()
        
        # Convert to response format
        refund_list = []
        for refund in refunds:
            refund_list.append(RefundResponse(
                id=refund.id,
                refund_id=refund.refund_id,
                payment_id=refund.payment_id,
                amount=refund.amount,
                reason=refund.reason,
                notes=refund.notes,
                refund_status=refund.refund_status,
                processed_by=refund.processed_by,
                created_at=refund.created_at,
                processed_at=refund.processed_at
            ))
        
        return refund_list
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
