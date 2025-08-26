import stripe
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.db.models.payment import Payment, PaymentStatus, PaymentMethod, Ticket, TicketType, DiscountCode, DiscountCodeUsage, Refund
from app.db.models.event import Event, EventRegistration
from app.db.models.models import User
from app.schemas.payment import PaymentCreate, PaymentUpdate, TicketCreate, DiscountCodeCreate, RefundCreate
from app.core.config import settings
import logging

# Configure Stripe
stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', 'sk_test_your_stripe_key')

logger = logging.getLogger(__name__)

class PaymentService:
    def __init__(self):
        pass
    
    def create_payment_intent(self, db: Session, payment_data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """Create payment intent with Stripe"""
        try:
            # Get event and ticket information
            event = db.query(Event).filter(Event.id == payment_data['event_id']).first()
            if not event:
                raise ValueError("Event not found")
            
            # Calculate amount based on ticket type and quantity
            ticket = db.query(Ticket).filter(
                Ticket.event_id == payment_data['event_id'],
                Ticket.ticket_type == payment_data['ticket_type']
            ).first()
            
            if not ticket:
                raise ValueError("Ticket type not found")
            
            if ticket.quantity_sold >= ticket.quantity_available:
                raise ValueError("Ticket sold out")
            
            # Calculate total amount
            base_amount = ticket.price * payment_data['quantity']
            
            # Apply discount if provided
            discount_amount = 0
            if payment_data.get('discount_code'):
                discount_amount = self._calculate_discount(
                    db, payment_data['discount_code'], base_amount, 
                    payment_data['event_id'], payment_data['ticket_type']
                )
            
            final_amount = base_amount - discount_amount
            
            # Create Stripe payment intent
            intent = stripe.PaymentIntent.create(
                amount=int(final_amount * 100),  # Stripe uses cents
                currency=payment_data.get('currency', 'idr').lower(),
                metadata={
                    'event_id': payment_data['event_id'],
                    'ticket_type': payment_data['ticket_type'],
                    'quantity': payment_data['quantity'],
                    'user_id': user_id,
                    'discount_code': payment_data.get('discount_code', '')
                }
            )
            
            # Create payment record
            payment = Payment(
                payment_id=intent.id,
                amount=final_amount,
                currency=payment_data.get('currency', 'IDR'),
                payment_method=PaymentMethod(payment_data['payment_method']),
                payment_status=PaymentStatus.PENDING,
                provider='stripe',
                provider_payment_id=intent.id,
                user_id=user_id,
                event_id=payment_data['event_id'],
                registration_id=0,  # Will be updated after registration
                description=f"Payment for {event.title} - {payment_data['ticket_type']}",
                payment_metadata=json.dumps({
                    'stripe_payment_intent_id': intent.id,
                    'ticket_type': payment_data['ticket_type'],
                    'quantity': payment_data['quantity'],
                    'discount_amount': discount_amount
                }),
                expired_at=datetime.utcnow() + timedelta(hours=24)
            )
            
            db.add(payment)
            db.commit()
            db.refresh(payment)
            
            return {
                'payment_intent_id': intent.id,
                'client_secret': intent.client_secret,
                'amount': final_amount,
                'currency': payment_data.get('currency', 'IDR'),
                'payment_id': payment.id,
                'expires_at': payment.expired_at
            }
            
        except Exception as e:
            logger.error(f"Error creating payment intent: {str(e)}")
            raise
    
    def process_payment_webhook(self, db: Session, event_data: Dict[str, Any]) -> bool:
        """Process Stripe webhook events"""
        try:
            event_type = event_data['type']
            payment_intent = event_data['data']['object']
            
            if event_type == 'payment_intent.succeeded':
                return self._handle_payment_success(db, payment_intent)
            elif event_type == 'payment_intent.payment_failed':
                return self._handle_payment_failed(db, payment_intent)
            elif event_type == 'payment_intent.canceled':
                return self._handle_payment_cancelled(db, payment_intent)
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing webhook: {str(e)}")
            return False
    
    def _handle_payment_success(self, db: Session, payment_intent: Dict[str, Any]) -> bool:
        """Handle successful payment"""
        try:
            payment = db.query(Payment).filter(
                Payment.provider_payment_id == payment_intent['id']
            ).first()
            
            if not payment:
                logger.error(f"Payment not found for intent: {payment_intent['id']}")
                return False
            
            # Update payment status
            payment.payment_status = PaymentStatus.SUCCESS
            payment.paid_at = datetime.utcnow()
            
            # Create event registration
            metadata = json.loads(payment.payment_metadata or '{}')
            registration = EventRegistration(
                event_id=payment.event_id,
                user_id=payment.user_id,
                status='confirmed',
                ticket_type=metadata.get('ticket_type', 'regular'),
                price_paid=payment.amount,
                payment_status='paid'
            )
            
            db.add(registration)
            db.commit()
            db.refresh(registration)
            
            # Update payment with registration ID
            payment.registration_id = registration.id
            
            # Update ticket sold count
            ticket = db.query(Ticket).filter(
                Ticket.event_id == payment.event_id,
                Ticket.ticket_type == metadata.get('ticket_type')
            ).first()
            
            if ticket:
                ticket.quantity_sold += metadata.get('quantity', 1)
            
            # Update event registration count
            event = db.query(Event).filter(Event.id == payment.event_id).first()
            if event:
                event.current_registrations += 1
            
            db.commit()
            
            # Send confirmation email (implement later)
            # self._send_payment_confirmation_email(payment, registration)
            
            return True
            
        except Exception as e:
            logger.error(f"Error handling payment success: {str(e)}")
            db.rollback()
            return False
    
    def _handle_payment_failed(self, db: Session, payment_intent: Dict[str, Any]) -> bool:
        """Handle failed payment"""
        try:
            payment = db.query(Payment).filter(
                Payment.provider_payment_id == payment_intent['id']
            ).first()
            
            if payment:
                payment.payment_status = PaymentStatus.FAILED
                db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error handling payment failed: {str(e)}")
            return False
    
    def _handle_payment_cancelled(self, db: Session, payment_intent: Dict[str, Any]) -> bool:
        """Handle cancelled payment"""
        try:
            payment = db.query(Payment).filter(
                Payment.provider_payment_id == payment_intent['id']
            ).first()
            
            if payment:
                payment.payment_status = PaymentStatus.CANCELLED
                db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error handling payment cancelled: {str(e)}")
            return False
    
    def _calculate_discount(self, db: Session, discount_code: str, amount: float, 
                          event_id: int, ticket_type: str) -> float:
        """Calculate discount amount"""
        try:
            discount = db.query(DiscountCode).filter(
                DiscountCode.code == discount_code,
                DiscountCode.is_active == True
            ).first()
            
            if not discount:
                return 0
            
            # Check validity period
            now = datetime.utcnow()
            if discount.valid_from and now < discount.valid_from:
                return 0
            if discount.valid_until and now > discount.valid_until:
                return 0
            
            # Check usage limits
            if discount.max_usage and discount.current_usage >= discount.max_usage:
                return 0
            
            # Check minimum amount
            if amount < discount.minimum_amount:
                return 0
            
            # Calculate discount
            if discount.discount_type == 'percentage':
                discount_amount = amount * (discount.discount_value / 100)
                if discount.maximum_discount:
                    discount_amount = min(discount_amount, discount.maximum_discount)
            else:
                discount_amount = discount.discount_value
            
            return discount_amount
            
        except Exception as e:
            logger.error(f"Error calculating discount: {str(e)}")
            return 0
    
    def create_ticket(self, db: Session, ticket_data: TicketCreate) -> Ticket:
        """Create new ticket type for event"""
        try:
            ticket = Ticket(
                ticket_type=TicketType(ticket_data.ticket_type),
                price=ticket_data.price,
                currency=ticket_data.currency,
                quantity_available=ticket_data.quantity_available,
                features=json.dumps(ticket_data.features) if ticket_data.features else None,
                description=ticket_data.description,
                sale_start_date=ticket_data.sale_start_date,
                sale_end_date=ticket_data.sale_end_date,
                event_id=ticket_data.event_id
            )
            
            db.add(ticket)
            db.commit()
            db.refresh(ticket)
            
            return ticket
            
        except Exception as e:
            logger.error(f"Error creating ticket: {str(e)}")
            db.rollback()
            raise
    
    def create_discount_code(self, db: Session, discount_data: DiscountCodeCreate, created_by: int) -> DiscountCode:
        """Create new discount code"""
        try:
            discount = DiscountCode(
                code=discount_data.code.upper(),
                discount_type=discount_data.discount_type,
                discount_value=discount_data.discount_value,
                minimum_amount=discount_data.minimum_amount,
                maximum_discount=discount_data.maximum_discount,
                max_usage=discount_data.max_usage,
                max_usage_per_user=discount_data.max_usage_per_user,
                valid_from=discount_data.valid_from,
                valid_until=discount_data.valid_until,
                applicable_events=json.dumps(discount_data.applicable_events) if discount_data.applicable_events else None,
                applicable_ticket_types=json.dumps(discount_data.applicable_ticket_types) if discount_data.applicable_ticket_types else None,
                created_by=created_by
            )
            
            db.add(discount)
            db.commit()
            db.refresh(discount)
            
            return discount
            
        except Exception as e:
            logger.error(f"Error creating discount code: {str(e)}")
            db.rollback()
            raise
    
    def get_payment_analytics(self, db: Session, user_id: Optional[int] = None, 
                            start_date: Optional[datetime] = None, 
                            end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get payment analytics"""
        try:
            query = db.query(Payment)
            
            if user_id:
                query = query.filter(Payment.user_id == user_id)
            
            if start_date:
                query = query.filter(Payment.created_at >= start_date)
            
            if end_date:
                query = query.filter(Payment.created_at <= end_date)
            
            payments = query.all()
            
            total_payments = len(payments)
            successful_payments = len([p for p in payments if p.payment_status == PaymentStatus.SUCCESS])
            failed_payments = len([p for p in payments if p.payment_status == PaymentStatus.FAILED])
            pending_payments = len([p for p in payments if p.payment_status == PaymentStatus.PENDING])
            
            total_revenue = sum(p.amount for p in payments if p.payment_status == PaymentStatus.SUCCESS)
            average_amount = total_revenue / successful_payments if successful_payments > 0 else 0
            
            # Payment methods distribution
            methods_distribution = {}
            for payment in payments:
                method = payment.payment_method.value
                methods_distribution[method] = methods_distribution.get(method, 0) + 1
            
            # Monthly revenue
            monthly_revenue = []
            for i in range(12):
                month_date = datetime.utcnow() - timedelta(days=30*i)
                month_payments = [p for p in payments 
                                if p.created_at.month == month_date.month 
                                and p.created_at.year == month_date.year
                                and p.payment_status == PaymentStatus.SUCCESS]
                
                monthly_revenue.append({
                    'month': month_date.strftime('%B %Y'),
                    'revenue': sum(p.amount for p in month_payments),
                    'count': len(month_payments)
                })
            
            return {
                'total_payments': total_payments,
                'total_revenue': total_revenue,
                'successful_payments': successful_payments,
                'failed_payments': failed_payments,
                'pending_payments': pending_payments,
                'average_payment_amount': average_amount,
                'payment_methods_distribution': methods_distribution,
                'monthly_revenue': monthly_revenue
            }
            
        except Exception as e:
            logger.error(f"Error getting payment analytics: {str(e)}")
            return {}
    
    def create_refund(self, db: Session, refund_data: RefundCreate, processed_by: int) -> Refund:
        """Create refund request"""
        try:
            payment = db.query(Payment).filter(Payment.id == refund_data.payment_id).first()
            if not payment:
                raise ValueError("Payment not found")
            
            if payment.payment_status != PaymentStatus.SUCCESS:
                raise ValueError("Payment is not successful")
            
            # Check if refund amount is valid
            if refund_data.amount > payment.amount:
                raise ValueError("Refund amount cannot exceed payment amount")
            
            refund = Refund(
                payment_id=refund_data.payment_id,
                amount=refund_data.amount,
                reason=refund_data.reason,
                notes=refund_data.notes,
                processed_by=processed_by
            )
            
            db.add(refund)
            db.commit()
            db.refresh(refund)
            
            return refund
            
        except Exception as e:
            logger.error(f"Error creating refund: {str(e)}")
            db.rollback()
            raise
