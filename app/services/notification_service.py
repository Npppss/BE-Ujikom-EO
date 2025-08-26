import json
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.db.models.notification import (
    Notification, NotificationType, NotificationPriority, NotificationStatus,
    NotificationTemplate, NotificationPreference, NotificationLog
)
from app.db.models.models import User
from app.db.models.event import Event, EventRegistration
from app.db.models.payment import Payment
from app.services.websocket_manager import manager
from app.services.email_service import EmailService
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.email_service = EmailService()
    
    async def create_notification(
        self, 
        db: Session, 
        user_id: int, 
        notification_type: NotificationType,
        title: str,
        message: str,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        event_id: Optional[int] = None,
        payment_id: Optional[int] = None,
        certificate_id: Optional[int] = None,
        action_url: Optional[str] = None,
        notification_metadata: Optional[Dict[str, Any]] = None,
        scheduled_at: Optional[datetime] = None
    ) -> Notification:
        """Create a new notification"""
        try:
            # Get user notification preferences
            preferences = db.query(NotificationPreference).filter(
                NotificationPreference.user_id == user_id
            ).first()
            
            if not preferences:
                # Create default preferences
                preferences = NotificationPreference(user_id=user_id)
                db.add(preferences)
                db.commit()
                db.refresh(preferences)
            
            # Check if user wants this type of notification
            if not self._should_send_notification(preferences, notification_type):
                logger.info(f"User {user_id} has disabled {notification_type.value} notifications")
                return None
            
            # Create notification
            notification = Notification(
                title=title,
                message=message,
                notification_type=notification_type,
                priority=priority,
                user_id=user_id,
                event_id=event_id,
                payment_id=payment_id,
                certificate_id=certificate_id,
                action_url=action_url,
                notification_metadata=json.dumps(notification_metadata) if notification_metadata else None,
                scheduled_at=scheduled_at,
                send_email=preferences.email_enabled,
                send_push=preferences.push_enabled,
                send_sms=preferences.sms_enabled,
                send_in_app=preferences.in_app_enabled
            )
            
            db.add(notification)
            db.commit()
            db.refresh(notification)
            
            # Send notification immediately if not scheduled
            if not scheduled_at or scheduled_at <= datetime.utcnow():
                await self._send_notification(db, notification)
            
            return notification
            
        except Exception as e:
            logger.error(f"Error creating notification: {str(e)}")
            db.rollback()
            raise
    
    async def _send_notification(self, db: Session, notification: Notification):
        """Send notification through all enabled channels"""
        try:
            # Send in-app notification
            if notification.send_in_app:
                await self._send_in_app_notification(notification)
            
            # Send email notification
            if notification.send_email:
                await self._send_email_notification(db, notification)
            
            # Send push notification
            if notification.send_push:
                await self._send_push_notification(notification)
            
            # Send SMS notification
            if notification.send_sms:
                await self._send_sms_notification(notification)
            
            # Update notification status
            notification.status = NotificationStatus.SENT
            notification.sent_at = datetime.utcnow()
            db.commit()
            
        except Exception as e:
            logger.error(f"Error sending notification {notification.id}: {str(e)}")
            notification.status = NotificationStatus.FAILED
            db.commit()
    
    async def _send_in_app_notification(self, notification: Notification):
        """Send in-app notification via WebSocket"""
        try:
            notification_data = {
                "id": notification.notification_id,
                "title": notification.title,
                "message": notification.message,
                "type": notification.notification_type.value,
                "priority": notification.priority.value,
                "action_url": notification.action_url,
                "created_at": notification.created_at.isoformat()
            }
            
            await manager.send_notification(notification.user_id, notification_data)
            logger.info(f"Sent in-app notification to user {notification.user_id}")
            
        except Exception as e:
            logger.error(f"Error sending in-app notification: {str(e)}")
    
    async def _send_email_notification(self, db: Session, notification: Notification):
        """Send email notification"""
        try:
            user = db.query(User).filter(User.id == notification.user_id).first()
            if not user:
                return
            
            # Get email template
            template = db.query(NotificationTemplate).filter(
                NotificationTemplate.notification_type == notification.notification_type,
                NotificationTemplate.is_active == True
            ).first()
            
            subject = notification.title
            body = notification.message
            
            if template and template.email_subject_template:
                subject = template.email_subject_template
            if template and template.email_body_template:
                body = template.email_body_template
            
            # Send email
            await self.email_service.send_notification_email(
                to_email=user.email,
                subject=subject,
                body=body,
                notification_data=notification
            )
            
            # Log email delivery
            self._log_delivery(db, notification.id, "email", "success")
            
        except Exception as e:
            logger.error(f"Error sending email notification: {str(e)}")
            self._log_delivery(db, notification.id, "email", "failed", str(e))
    
    async def _send_push_notification(self, notification: Notification):
        """Send push notification (placeholder for Firebase/APNS integration)"""
        try:
            # This would integrate with Firebase Cloud Messaging or Apple Push Notification Service
            # For now, just log the action
            logger.info(f"Push notification would be sent to user {notification.user_id}")
            
        except Exception as e:
            logger.error(f"Error sending push notification: {str(e)}")
    
    async def _send_sms_notification(self, notification: Notification):
        """Send SMS notification (placeholder for Twilio integration)"""
        try:
            # This would integrate with Twilio or other SMS service
            # For now, just log the action
            logger.info(f"SMS notification would be sent to user {notification.user_id}")
            
        except Exception as e:
            logger.error(f"Error sending SMS notification: {str(e)}")
    
    def _should_send_notification(self, preferences: NotificationPreference, notification_type: NotificationType) -> bool:
        """Check if notification should be sent based on user preferences"""
        if notification_type == NotificationType.EVENT_REMINDER:
            return preferences.event_reminders
        elif notification_type in [NotificationType.PAYMENT_SUCCESS, NotificationType.PAYMENT_FAILED]:
            return preferences.payment_notifications
        elif notification_type in [NotificationType.EVENT_UPDATE, NotificationType.EVENT_CANCELLED]:
            return preferences.event_updates
        elif notification_type == NotificationType.SYSTEM_ANNOUNCEMENT:
            return preferences.system_announcements
        elif notification_type == NotificationType.CERTIFICATE_READY:
            return preferences.certificate_notifications
        
        return True
    
    def _log_delivery(self, db: Session, notification_id: int, channel: str, status: str, error_message: Optional[str] = None):
        """Log notification delivery attempt"""
        try:
            log = NotificationLog(
                notification_id=notification_id,
                channel=channel,
                status=status,
                error_message=error_message
            )
            db.add(log)
            db.commit()
        except Exception as e:
            logger.error(f"Error logging delivery: {str(e)}")
    
    async def send_event_reminder(self, db: Session, event_id: int, reminder_type: str = "day_before"):
        """Send event reminder to registered participants"""
        try:
            event = db.query(Event).filter(Event.id == event_id).first()
            if not event:
                return
            
            # Get registered participants
            registrations = db.query(EventRegistration).filter(
                EventRegistration.event_id == event_id,
                EventRegistration.status == "confirmed"
            ).all()
            
            for registration in registrations:
                title = f"Reminder: {event.title}"
                message = f"Don't forget! {event.title} is happening tomorrow at {event.start_time.strftime('%H:%M')}."
                
                if reminder_type == "hour_before":
                    title = f"Starting Soon: {event.title}"
                    message = f"{event.title} starts in 1 hour!"
                
                await self.create_notification(
                    db=db,
                    user_id=registration.user_id,
                    notification_type=NotificationType.EVENT_REMINDER,
                    title=title,
                    message=message,
                    priority=NotificationPriority.HIGH,
                    event_id=event_id,
                    action_url=f"/events/{event_id}"
                )
            
            logger.info(f"Sent {reminder_type} reminders for event {event_id} to {len(registrations)} participants")
            
        except Exception as e:
            logger.error(f"Error sending event reminders: {str(e)}")
    
    async def send_payment_notification(self, db: Session, payment_id: int, notification_type: NotificationType):
        """Send payment-related notification"""
        try:
            payment = db.query(Payment).filter(Payment.id == payment_id).first()
            if not payment:
                return
            
            user = db.query(User).filter(User.id == payment.user_id).first()
            event = db.query(Event).filter(Event.id == payment.event_id).first()
            
            if notification_type == NotificationType.PAYMENT_SUCCESS:
                title = "Payment Successful!"
                message = f"Your payment of {payment.currency} {payment.amount:,.0f} for {event.title} has been confirmed."
                priority = NotificationPriority.MEDIUM
            elif notification_type == NotificationType.PAYMENT_FAILED:
                title = "Payment Failed"
                message = f"Your payment for {event.title} was unsuccessful. Please try again."
                priority = NotificationPriority.HIGH
            else:
                return
            
            await self.create_notification(
                db=db,
                user_id=payment.user_id,
                notification_type=notification_type,
                title=title,
                message=message,
                priority=priority,
                payment_id=payment_id,
                event_id=payment.event_id,
                action_url=f"/payments/{payment_id}"
            )
            
        except Exception as e:
            logger.error(f"Error sending payment notification: {str(e)}")
    
    async def send_event_update_notification(self, db: Session, event_id: int, update_type: str, update_details: str):
        """Send event update notification to participants"""
        try:
            event = db.query(Event).filter(Event.id == event_id).first()
            if not event:
                return
            
            # Get registered participants
            registrations = db.query(EventRegistration).filter(
                EventRegistration.event_id == event_id,
                EventRegistration.status == "confirmed"
            ).all()
            
            title = f"Event Update: {event.title}"
            message = f"Update for {event.title}: {update_details}"
            priority = NotificationPriority.MEDIUM
            
            if update_type == "cancelled":
                title = f"Event Cancelled: {event.title}"
                message = f"{event.title} has been cancelled. We apologize for any inconvenience."
                priority = NotificationPriority.HIGH
            
            for registration in registrations:
                await self.create_notification(
                    db=db,
                    user_id=registration.user_id,
                    notification_type=NotificationType.EVENT_UPDATE,
                    title=title,
                    message=message,
                    priority=priority,
                    event_id=event_id,
                    action_url=f"/events/{event_id}"
                )
            
            logger.info(f"Sent event update notifications to {len(registrations)} participants")
            
        except Exception as e:
            logger.error(f"Error sending event update notifications: {str(e)}")
    
    def get_user_notifications(self, db: Session, user_id: int, limit: int = 50, offset: int = 0) -> List[Notification]:
        """Get notifications for a user"""
        try:
            notifications = db.query(Notification).filter(
                Notification.user_id == user_id
            ).order_by(desc(Notification.created_at)).offset(offset).limit(limit).all()
            
            return notifications
            
        except Exception as e:
            logger.error(f"Error getting user notifications: {str(e)}")
            return []
    
    def mark_notification_read(self, db: Session, notification_id: str, user_id: int) -> bool:
        """Mark notification as read"""
        try:
            notification = db.query(Notification).filter(
                Notification.notification_id == notification_id,
                Notification.user_id == user_id
            ).first()
            
            if notification:
                notification.status = NotificationStatus.READ
                notification.read_at = datetime.utcnow()
                db.commit()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error marking notification as read: {str(e)}")
            return False
    
    def get_unread_count(self, db: Session, user_id: int) -> int:
        """Get count of unread notifications for user"""
        try:
            count = db.query(Notification).filter(
                Notification.user_id == user_id,
                Notification.status == NotificationStatus.SENT
            ).count()
            
            return count
            
        except Exception as e:
            logger.error(f"Error getting unread count: {str(e)}")
            return 0
    
    async def send_bulk_notification(self, db: Session, user_ids: List[int], title: str, message: str, 
                                   notification_type: NotificationType = NotificationType.SYSTEM_ANNOUNCEMENT):
        """Send notification to multiple users"""
        try:
            for user_id in user_ids:
                await self.create_notification(
                    db=db,
                    user_id=user_id,
                    notification_type=notification_type,
                    title=title,
                    message=message,
                    priority=NotificationPriority.MEDIUM
                )
            
            logger.info(f"Sent bulk notification to {len(user_ids)} users")
            
        except Exception as e:
            logger.error(f"Error sending bulk notification: {str(e)}")
    
    def update_notification_preferences(self, db: Session, user_id: int, preferences: Dict[str, Any]) -> bool:
        """Update user notification preferences"""
        try:
            user_preferences = db.query(NotificationPreference).filter(
                NotificationPreference.user_id == user_id
            ).first()
            
            if not user_preferences:
                user_preferences = NotificationPreference(user_id=user_id)
                db.add(user_preferences)
            
            # Update preferences
            for key, value in preferences.items():
                if hasattr(user_preferences, key):
                    setattr(user_preferences, key, value)
            
            db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error updating notification preferences: {str(e)}")
            db.rollback()
            return False
