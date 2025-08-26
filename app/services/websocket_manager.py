import json
import asyncio
from typing import Dict, List, Set, Optional
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # Store active connections: {user_id: WebSocket}
        self.active_connections: Dict[int, WebSocket] = {}
        # Store user connection info: {user_id: {"ws": WebSocket, "last_ping": datetime}}
        self.connection_info: Dict[int, Dict] = {}
        # Store pending notifications: {user_id: List[notification_data]}
        self.pending_notifications: Dict[int, List[Dict]] = {}
        
    async def connect(self, websocket: WebSocket, user_id: int):
        """Connect a new WebSocket client"""
        try:
            await websocket.accept()
            self.active_connections[user_id] = websocket
            self.connection_info[user_id] = {
                "ws": websocket,
                "last_ping": datetime.utcnow(),
                "connected_at": datetime.utcnow()
            }
            
            # Send any pending notifications
            if user_id in self.pending_notifications:
                for notification in self.pending_notifications[user_id]:
                    await self.send_personal_message(notification, user_id)
                self.pending_notifications[user_id] = []
            
            logger.info(f"User {user_id} connected to WebSocket")
            
        except Exception as e:
            logger.error(f"Error connecting user {user_id}: {str(e)}")
    
    def disconnect(self, user_id: int):
        """Disconnect a WebSocket client"""
        try:
            if user_id in self.active_connections:
                del self.active_connections[user_id]
            if user_id in self.connection_info:
                del self.connection_info[user_id]
            logger.info(f"User {user_id} disconnected from WebSocket")
        except Exception as e:
            logger.error(f"Error disconnecting user {user_id}: {str(e)}")
    
    async def send_personal_message(self, message: Dict, user_id: int):
        """Send message to specific user"""
        try:
            if user_id in self.active_connections:
                websocket = self.active_connections[user_id]
                await websocket.send_text(json.dumps(message))
                logger.debug(f"Sent message to user {user_id}: {message}")
            else:
                # Store message for when user reconnects
                if user_id not in self.pending_notifications:
                    self.pending_notifications[user_id] = []
                self.pending_notifications[user_id].append(message)
                logger.debug(f"Stored pending message for user {user_id}")
        except Exception as e:
            logger.error(f"Error sending message to user {user_id}: {str(e)}")
            # Remove failed connection
            self.disconnect(user_id)
    
    async def broadcast(self, message: Dict, exclude_user: Optional[int] = None):
        """Broadcast message to all connected users"""
        try:
            disconnected_users = []
            for user_id, websocket in self.active_connections.items():
                if user_id != exclude_user:
                    try:
                        await websocket.send_text(json.dumps(message))
                    except Exception as e:
                        logger.error(f"Error broadcasting to user {user_id}: {str(e)}")
                        disconnected_users.append(user_id)
            
            # Clean up disconnected users
            for user_id in disconnected_users:
                self.disconnect(user_id)
                
        except Exception as e:
            logger.error(f"Error broadcasting message: {str(e)}")
    
    async def send_notification(self, user_id: int, notification_data: Dict):
        """Send notification to specific user"""
        message = {
            "type": "notification",
            "data": notification_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.send_personal_message(message, user_id)
    
    async def send_event_update(self, event_id: int, update_data: Dict, user_ids: List[int]):
        """Send event update to multiple users"""
        message = {
            "type": "event_update",
            "event_id": event_id,
            "data": update_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        for user_id in user_ids:
            await self.send_personal_message(message, user_id)
    
    async def send_payment_update(self, user_id: int, payment_data: Dict):
        """Send payment update to user"""
        message = {
            "type": "payment_update",
            "data": payment_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await self.send_personal_message(message, user_id)
    
    async def send_attendance_update(self, event_id: int, attendance_data: Dict, user_ids: List[int]):
        """Send attendance update to multiple users"""
        message = {
            "type": "attendance_update",
            "event_id": event_id,
            "data": attendance_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        for user_id in user_ids:
            await self.send_personal_message(message, user_id)
    
    def get_connected_users(self) -> List[int]:
        """Get list of connected user IDs"""
        return list(self.active_connections.keys())
    
    def is_user_connected(self, user_id: int) -> bool:
        """Check if user is connected"""
        return user_id in self.active_connections
    
    async def ping_all(self):
        """Ping all connected clients to check connection health"""
        try:
            disconnected_users = []
            for user_id, websocket in self.active_connections.items():
                try:
                    await websocket.send_text(json.dumps({"type": "ping", "timestamp": datetime.utcnow().isoformat()}))
                    self.connection_info[user_id]["last_ping"] = datetime.utcnow()
                except Exception as e:
                    logger.error(f"Error pinging user {user_id}: {str(e)}")
                    disconnected_users.append(user_id)
            
            # Clean up disconnected users
            for user_id in disconnected_users:
                self.disconnect(user_id)
                
        except Exception as e:
            logger.error(f"Error pinging all users: {str(e)}")
    
    async def cleanup_inactive_connections(self, timeout_minutes: int = 30):
        """Clean up inactive connections"""
        try:
            current_time = datetime.utcnow()
            disconnected_users = []
            
            for user_id, info in self.connection_info.items():
                time_diff = (current_time - info["last_ping"]).total_seconds() / 60
                if time_diff > timeout_minutes:
                    disconnected_users.append(user_id)
            
            for user_id in disconnected_users:
                self.disconnect(user_id)
                logger.info(f"Cleaned up inactive connection for user {user_id}")
                
        except Exception as e:
            logger.error(f"Error cleaning up inactive connections: {str(e)}")

# Global connection manager instance
manager = ConnectionManager()

class WebSocketHandler:
    def __init__(self):
        self.manager = manager
    
    async def handle_websocket(self, websocket: WebSocket, user_id: int):
        """Handle WebSocket connection for a user"""
        await self.manager.connect(websocket, user_id)
        
        try:
            while True:
                # Wait for messages from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                await self.handle_message(user_id, message)
                
        except WebSocketDisconnect:
            self.manager.disconnect(user_id)
        except Exception as e:
            logger.error(f"Error handling WebSocket for user {user_id}: {str(e)}")
            self.manager.disconnect(user_id)
    
    async def handle_message(self, user_id: int, message: Dict):
        """Handle incoming WebSocket message"""
        try:
            message_type = message.get("type")
            
            if message_type == "ping":
                # Handle ping from client
                await self.manager.send_personal_message({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                }, user_id)
            
            elif message_type == "notification_read":
                # Handle notification read acknowledgment
                notification_id = message.get("notification_id")
                await self.mark_notification_read(user_id, notification_id)
            
            elif message_type == "subscribe_event":
                # Handle event subscription
                event_id = message.get("event_id")
                await self.subscribe_to_event(user_id, event_id)
            
            elif message_type == "unsubscribe_event":
                # Handle event unsubscription
                event_id = message.get("event_id")
                await self.unsubscribe_from_event(user_id, event_id)
            
            else:
                logger.warning(f"Unknown message type from user {user_id}: {message_type}")
                
        except Exception as e:
            logger.error(f"Error handling message from user {user_id}: {str(e)}")
    
    async def mark_notification_read(self, user_id: int, notification_id: str):
        """Mark notification as read"""
        # This would typically update the database
        # For now, just log the action
        logger.info(f"User {user_id} marked notification {notification_id} as read")
    
    async def subscribe_to_event(self, user_id: int, event_id: int):
        """Subscribe user to event updates"""
        # This would typically store the subscription in database
        logger.info(f"User {user_id} subscribed to event {event_id}")
    
    async def unsubscribe_from_event(self, user_id: int, event_id: int):
        """Unsubscribe user from event updates"""
        # This would typically remove the subscription from database
        logger.info(f"User {user_id} unsubscribed from event {event_id}")

# Global WebSocket handler instance
websocket_handler = WebSocketHandler()
