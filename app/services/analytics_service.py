import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, extract
from app.db.models.event import Event, EventRegistration, EventStatus, EventCategory, Attendance
from app.db.models.payment import Payment, PaymentStatus, PaymentMethod
from app.db.models.models import User, Role
from app.db.models.certificate import Certificate
from app.db.models.notification import Notification, NotificationType
import logging

logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(self):
        pass
    
    def get_dashboard_overview(self, db: Session, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Get comprehensive dashboard overview"""
        try:
            # Base query filters
            event_filter = Event.is_active == True
            if user_id:
                event_filter = and_(event_filter, Event.organizer_id == user_id)
            
            # Event statistics
            total_events = db.query(Event).filter(event_filter).count()
            published_events = db.query(Event).filter(
                and_(event_filter, Event.status == EventStatus.PUBLISHED)
            ).count()
            ongoing_events = db.query(Event).filter(
                and_(event_filter, Event.status == EventStatus.ONGOING)
            ).count()
            completed_events = db.query(Event).filter(
                and_(event_filter, Event.status == EventStatus.COMPLETED)
            ).count()
            
            # Registration statistics
            if user_id:
                reg_filter = EventRegistration.user_id == user_id
            else:
                reg_filter = True
            
            total_registrations = db.query(EventRegistration).filter(reg_filter).count()
            confirmed_registrations = db.query(EventRegistration).filter(
                and_(reg_filter, EventRegistration.status == "confirmed")
            ).count()
            
            # Attendance statistics
            if user_id:
                att_filter = Attendance.user_id == user_id
            else:
                att_filter = True
            
            total_attendances = db.query(Attendance).filter(
                and_(att_filter, Attendance.check_in_time.isnot(None))
            ).count()
            
            # Payment statistics
            if user_id:
                pay_filter = Payment.user_id == user_id
            else:
                pay_filter = True
            
            total_payments = db.query(Payment).filter(pay_filter).count()
            successful_payments = db.query(Payment).filter(
                and_(pay_filter, Payment.payment_status == PaymentStatus.SUCCESS)
            ).count()
            total_revenue = db.query(func.sum(Payment.amount)).filter(
                and_(pay_filter, Payment.payment_status == PaymentStatus.SUCCESS)
            ).scalar() or 0
            
            # User statistics
            total_users = db.query(User).count()
            active_users = db.query(User).filter(User.is_active == True).count()
            verified_users = db.query(User).filter(User.is_verified == True).count()
            
            return {
                "events": {
                    "total": total_events,
                    "published": published_events,
                    "ongoing": ongoing_events,
                    "completed": completed_events
                },
                "registrations": {
                    "total": total_registrations,
                    "confirmed": confirmed_registrations,
                    "confirmation_rate": (confirmed_registrations / total_registrations * 100) if total_registrations > 0 else 0
                },
                "attendance": {
                    "total": total_attendances,
                    "attendance_rate": (total_attendances / confirmed_registrations * 100) if confirmed_registrations > 0 else 0
                },
                "payments": {
                    "total": total_payments,
                    "successful": successful_payments,
                    "success_rate": (successful_payments / total_payments * 100) if total_payments > 0 else 0,
                    "total_revenue": total_revenue
                },
                "users": {
                    "total": total_users,
                    "active": active_users,
                    "verified": verified_users,
                    "verification_rate": (verified_users / total_users * 100) if total_users > 0 else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting dashboard overview: {str(e)}")
            return {}
    
    def get_event_analytics(self, db: Session, event_id: int) -> Dict[str, Any]:
        """Get detailed analytics for a specific event"""
        try:
            event = db.query(Event).filter(Event.id == event_id).first()
            if not event:
                return {}
            
            # Registration analytics
            registrations = db.query(EventRegistration).filter(
                EventRegistration.event_id == event_id
            ).all()
            
            total_registrations = len(registrations)
            confirmed_registrations = len([r for r in registrations if r.status == "confirmed"])
            waitlisted_registrations = len([r for r in registrations if r.status == "waitlisted"])
            
            # Attendance analytics
            attendances = db.query(Attendance).filter(
                Attendance.event_id == event_id
            ).all()
            
            total_attendances = len([a for a in attendances if a.check_in_time])
            check_outs = len([a for a in attendances if a.check_out_time])
            
            # Payment analytics
            payments = db.query(Payment).filter(Payment.event_id == event_id).all()
            
            total_payments = len(payments)
            successful_payments = len([p for p in payments if p.payment_status == PaymentStatus.SUCCESS])
            total_revenue = sum(p.amount for p in payments if p.payment_status == PaymentStatus.SUCCESS)
            
            # Payment method distribution
            payment_methods = {}
            for payment in payments:
                method = payment.payment_method.value
                payment_methods[method] = payment_methods.get(method, 0) + 1
            
            # Registration timeline
            registration_timeline = []
            for i in range(30):  # Last 30 days
                date = datetime.utcnow() - timedelta(days=i)
                daily_registrations = len([
                    r for r in registrations 
                    if r.created_at.date() == date.date()
                ])
                registration_timeline.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "count": daily_registrations
                })
            
            registration_timeline.reverse()
            
            # Attendance timeline
            attendance_timeline = []
            if event.start_date:
                event_date = event.start_date
                for hour in range(24):
                    hour_time = event_date.replace(hour=hour)
                    hourly_attendances = len([
                        a for a in attendances 
                        if a.check_in_time and a.check_in_time.hour == hour
                    ])
                    attendance_timeline.append({
                        "hour": hour,
                        "count": hourly_attendances
                    })
            
            return {
                "event_info": {
                    "id": event.id,
                    "title": event.title,
                    "category": event.category.value,
                    "status": event.status.value,
                    "start_date": event.start_date,
                    "end_date": event.end_date,
                    "location": event.location,
                    "max_capacity": event.max_capacity
                },
                "registrations": {
                    "total": total_registrations,
                    "confirmed": confirmed_registrations,
                    "waitlisted": waitlisted_registrations,
                    "confirmation_rate": (confirmed_registrations / total_registrations * 100) if total_registrations > 0 else 0,
                    "capacity_utilization": (confirmed_registrations / event.max_capacity * 100) if event.max_capacity else 0,
                    "timeline": registration_timeline
                },
                "attendance": {
                    "total": total_attendances,
                    "check_outs": check_outs,
                    "attendance_rate": (total_attendances / confirmed_registrations * 100) if confirmed_registrations > 0 else 0,
                    "timeline": attendance_timeline
                },
                "payments": {
                    "total": total_payments,
                    "successful": successful_payments,
                    "success_rate": (successful_payments / total_payments * 100) if total_payments > 0 else 0,
                    "total_revenue": total_revenue,
                    "average_ticket_price": (total_revenue / successful_payments) if successful_payments > 0 else 0,
                    "payment_methods": payment_methods
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting event analytics: {str(e)}")
            return {}
    
    def get_revenue_analytics(self, db: Session, user_id: Optional[int] = None, 
                            start_date: Optional[datetime] = None, 
                            end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get revenue analytics"""
        try:
            # Build query filters
            payment_filter = Payment.payment_status == PaymentStatus.SUCCESS
            
            if user_id:
                payment_filter = and_(payment_filter, Payment.user_id == user_id)
            
            if start_date:
                payment_filter = and_(payment_filter, Payment.created_at >= start_date)
            
            if end_date:
                payment_filter = and_(payment_filter, Payment.created_at <= end_date)
            
            # Get payments
            payments = db.query(Payment).filter(payment_filter).all()
            
            # Calculate metrics
            total_revenue = sum(p.amount for p in payments)
            total_transactions = len(payments)
            average_transaction = total_revenue / total_transactions if total_transactions > 0 else 0
            
            # Payment method distribution
            payment_methods = {}
            for payment in payments:
                method = payment.payment_method.value
                if method not in payment_methods:
                    payment_methods[method] = {"count": 0, "amount": 0}
                payment_methods[method]["count"] += 1
                payment_methods[method]["amount"] += payment.amount
            
            # Monthly revenue
            monthly_revenue = []
            for i in range(12):
                month_date = datetime.utcnow() - timedelta(days=30*i)
                month_payments = [
                    p for p in payments 
                    if p.created_at.month == month_date.month and p.created_at.year == month_date.year
                ]
                
                monthly_revenue.append({
                    "month": month_date.strftime("%B %Y"),
                    "revenue": sum(p.amount for p in month_payments),
                    "transactions": len(month_payments)
                })
            
            # Daily revenue (last 30 days)
            daily_revenue = []
            for i in range(30):
                date = datetime.utcnow() - timedelta(days=i)
                day_payments = [
                    p for p in payments 
                    if p.created_at.date() == date.date()
                ]
                
                daily_revenue.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "revenue": sum(p.amount for p in day_payments),
                    "transactions": len(day_payments)
                })
            
            daily_revenue.reverse()
            
            # Top events by revenue
            event_revenue = {}
            for payment in payments:
                event_id = payment.event_id
                if event_id not in event_revenue:
                    event_revenue[event_id] = {"amount": 0, "transactions": 0}
                event_revenue[event_id]["amount"] += payment.amount
                event_revenue[event_id]["transactions"] += 1
            
            top_events = []
            for event_id, data in sorted(event_revenue.items(), key=lambda x: x[1]["amount"], reverse=True)[:10]:
                event = db.query(Event).filter(Event.id == event_id).first()
                if event:
                    top_events.append({
                        "event_id": event_id,
                        "title": event.title,
                        "revenue": data["amount"],
                        "transactions": data["transactions"]
                    })
            
            return {
                "overview": {
                    "total_revenue": total_revenue,
                    "total_transactions": total_transactions,
                    "average_transaction": average_transaction
                },
                "payment_methods": payment_methods,
                "monthly_revenue": monthly_revenue,
                "daily_revenue": daily_revenue,
                "top_events": top_events
            }
            
        except Exception as e:
            logger.error(f"Error getting revenue analytics: {str(e)}")
            return {}
    
    def get_user_analytics(self, db: Session, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Get user analytics"""
        try:
            # Build query filters
            user_filter = User.is_active == True
            if user_id:
                user_filter = and_(user_filter, User.id == user_id)
            
            # User statistics
            total_users = db.query(User).filter(user_filter).count()
            verified_users = db.query(User).filter(
                and_(user_filter, User.is_verified == True)
            ).count()
            
            # User registration by role
            role_stats = {}
            users = db.query(User).filter(user_filter).all()
            
            for user in users:
                role_name = user.role.name
                if role_name not in role_stats:
                    role_stats[role_name] = {"count": 0, "verified": 0}
                role_stats[role_name]["count"] += 1
                if user.is_verified:
                    role_stats[role_name]["verified"] += 1
            
            # User activity
            active_users = []
            for user in users:
                # Count registrations
                registrations = db.query(EventRegistration).filter(
                    EventRegistration.user_id == user.id
                ).count()
                
                # Count attendances
                attendances = db.query(Attendance).filter(
                    Attendance.user_id == user.id,
                    Attendance.check_in_time.isnot(None)
                ).count()
                
                # Count payments
                payments = db.query(Payment).filter(
                    Payment.user_id == user.id,
                    Payment.payment_status == PaymentStatus.SUCCESS
                ).count()
                
                # Total spent
                total_spent = db.query(func.sum(Payment.amount)).filter(
                    Payment.user_id == user.id,
                    Payment.payment_status == PaymentStatus.SUCCESS
                ).scalar() or 0
                
                active_users.append({
                    "user_id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role.name,
                    "registrations": registrations,
                    "attendances": attendances,
                    "payments": payments,
                    "total_spent": total_spent,
                    "last_activity": user.updated_at
                })
            
            # Sort by activity
            active_users.sort(key=lambda x: x["registrations"] + x["attendances"], reverse=True)
            
            # User growth over time
            user_growth = []
            for i in range(12):
                month_date = datetime.utcnow() - timedelta(days=30*i)
                month_users = [
                    u for u in users 
                    if u.created_at.month == month_date.month and u.created_at.year == month_date.year
                ]
                
                user_growth.append({
                    "month": month_date.strftime("%B %Y"),
                    "new_users": len(month_users),
                    "verified_users": len([u for u in month_users if u.is_verified])
                })
            
            return {
                "overview": {
                    "total_users": total_users,
                    "verified_users": verified_users,
                    "verification_rate": (verified_users / total_users * 100) if total_users > 0 else 0
                },
                "role_distribution": role_stats,
                "active_users": active_users[:20],  # Top 20 most active users
                "user_growth": user_growth
            }
            
        except Exception as e:
            logger.error(f"Error getting user analytics: {str(e)}")
            return {}
    
    def get_event_category_analytics(self, db: Session) -> Dict[str, Any]:
        """Get analytics by event category"""
        try:
            categories = {}
            
            # Get all events
            events = db.query(Event).filter(Event.is_active == True).all()
            
            for event in events:
                category = event.category.value
                if category not in categories:
                    categories[category] = {
                        "total_events": 0,
                        "published_events": 0,
                        "ongoing_events": 0,
                        "completed_events": 0,
                        "total_registrations": 0,
                        "total_attendances": 0,
                        "total_revenue": 0
                    }
                
                categories[category]["total_events"] += 1
                
                if event.status == EventStatus.PUBLISHED:
                    categories[category]["published_events"] += 1
                elif event.status == EventStatus.ONGOING:
                    categories[category]["ongoing_events"] += 1
                elif event.status == EventStatus.COMPLETED:
                    categories[category]["completed_events"] += 1
                
                # Get registrations for this event
                registrations = db.query(EventRegistration).filter(
                    EventRegistration.event_id == event.id,
                    EventRegistration.status == "confirmed"
                ).count()
                categories[category]["total_registrations"] += registrations
                
                # Get attendances for this event
                attendances = db.query(Attendance).filter(
                    Attendance.event_id == event.id,
                    Attendance.check_in_time.isnot(None)
                ).count()
                categories[category]["total_attendances"] += attendances
                
                # Get revenue for this event
                revenue = db.query(func.sum(Payment.amount)).filter(
                    Payment.event_id == event.id,
                    Payment.payment_status == PaymentStatus.SUCCESS
                ).scalar() or 0
                categories[category]["total_revenue"] += revenue
            
            # Calculate averages and rates
            for category in categories:
                data = categories[category]
                data["average_registrations"] = data["total_registrations"] / data["total_events"] if data["total_events"] > 0 else 0
                data["average_attendances"] = data["total_attendances"] / data["total_events"] if data["total_events"] > 0 else 0
                data["average_revenue"] = data["total_revenue"] / data["total_events"] if data["total_events"] > 0 else 0
                data["attendance_rate"] = (data["total_attendances"] / data["total_registrations"] * 100) if data["total_registrations"] > 0 else 0
            
            return {
                "categories": categories,
                "top_categories_by_revenue": sorted(
                    categories.items(), 
                    key=lambda x: x[1]["total_revenue"], 
                    reverse=True
                )[:5],
                "top_categories_by_events": sorted(
                    categories.items(), 
                    key=lambda x: x[1]["total_events"], 
                    reverse=True
                )[:5]
            }
            
        except Exception as e:
            logger.error(f"Error getting category analytics: {str(e)}")
            return {}
    
    def get_notification_analytics(self, db: Session, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Get notification analytics"""
        try:
            # Build query filters
            notification_filter = True
            if user_id:
                notification_filter = Notification.user_id == user_id
            
            # Get notifications
            notifications = db.query(Notification).filter(notification_filter).all()
            
            # Notification statistics
            total_notifications = len(notifications)
            sent_notifications = len([n for n in notifications if n.status == NotificationStatus.SENT])
            read_notifications = len([n for n in notifications if n.status == NotificationStatus.READ])
            failed_notifications = len([n for n in notifications if n.status == NotificationStatus.FAILED])
            
            # Notification types distribution
            type_distribution = {}
            for notification in notifications:
                notification_type = notification.notification_type.value
                type_distribution[notification_type] = type_distribution.get(notification_type, 0) + 1
            
            # Notification priority distribution
            priority_distribution = {}
            for notification in notifications:
                priority = notification.priority.value
                priority_distribution[priority] = priority_distribution.get(priority, 0) + 1
            
            # Delivery channel statistics
            email_sent = len([n for n in notifications if n.email_sent])
            push_sent = len([n for n in notifications if n.push_sent])
            sms_sent = len([n for n in notifications if n.sms_sent])
            in_app_sent = len([n for n in notifications if n.in_app_sent])
            
            # Daily notification volume
            daily_volume = []
            for i in range(30):
                date = datetime.utcnow() - timedelta(days=i)
                daily_notifications = [
                    n for n in notifications 
                    if n.created_at.date() == date.date()
                ]
                
                daily_volume.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "sent": len([n for n in daily_notifications if n.status == NotificationStatus.SENT]),
                    "read": len([n for n in daily_notifications if n.status == NotificationStatus.READ]),
                    "failed": len([n for n in daily_notifications if n.status == NotificationStatus.FAILED])
                })
            
            daily_volume.reverse()
            
            return {
                "overview": {
                    "total": total_notifications,
                    "sent": sent_notifications,
                    "read": read_notifications,
                    "failed": failed_notifications,
                    "delivery_rate": (sent_notifications / total_notifications * 100) if total_notifications > 0 else 0,
                    "read_rate": (read_notifications / sent_notifications * 100) if sent_notifications > 0 else 0
                },
                "type_distribution": type_distribution,
                "priority_distribution": priority_distribution,
                "delivery_channels": {
                    "email": email_sent,
                    "push": push_sent,
                    "sms": sms_sent,
                    "in_app": in_app_sent
                },
                "daily_volume": daily_volume
            }
            
        except Exception as e:
            logger.error(f"Error getting notification analytics: {str(e)}")
            return {}

