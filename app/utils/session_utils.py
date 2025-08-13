from datetime import datetime, timedelta
from typing import Dict, Optional
from app.core.config import ADMIN_SESSION_TIMEOUT_MINUTES, USER_SESSION_TIMEOUT_MINUTES

def get_session_timeout_minutes(role: str) -> int:
    """
    Get session timeout in minutes based on user role
    
    Args:
        role (str): User role (admin, organizer, user)
        
    Returns:
        int: Session timeout in minutes
    """
    if role in ["admin", "organizer"]:
        return ADMIN_SESSION_TIMEOUT_MINUTES
    else:
        return USER_SESSION_TIMEOUT_MINUTES

def calculate_session_expiry(role: str, start_time: datetime = None) -> datetime:
    """
    Calculate when the session will expire
    
    Args:
        role (str): User role
        start_time (datetime): Session start time (defaults to current time)
        
    Returns:
        datetime: Session expiry time
    """
    if start_time is None:
        start_time = datetime.utcnow()
    
    timeout_minutes = get_session_timeout_minutes(role)
    return start_time + timedelta(minutes=timeout_minutes)

def get_remaining_session_time(expiry_time: datetime) -> Dict[str, int]:
    """
    Calculate remaining session time
    
    Args:
        expiry_time (datetime): When the session expires
        
    Returns:
        Dict: Dictionary with remaining time in different units
    """
    now = datetime.utcnow()
    remaining = expiry_time - now
    
    if remaining.total_seconds() <= 0:
        return {
            "expired": True,
            "remaining_seconds": 0,
            "remaining_minutes": 0,
            "remaining_hours": 0
        }
    
    return {
        "expired": False,
        "remaining_seconds": int(remaining.total_seconds()),
        "remaining_minutes": int(remaining.total_seconds() // 60),
        "remaining_hours": int(remaining.total_seconds() // 3600)
    }

def is_session_expired(expiry_time: datetime) -> bool:
    """
    Check if session is expired
    
    Args:
        expiry_time (datetime): When the session expires
        
    Returns:
        bool: True if expired, False otherwise
    """
    return datetime.utcnow() >= expiry_time

def format_session_timeout_message(role: str) -> str:
    """
    Get formatted message for session timeout
    
    Args:
        role (str): User role
        
    Returns:
        str: Formatted timeout message
    """
    timeout_minutes = get_session_timeout_minutes(role)
    
    if role in ["admin", "organizer"]:
        return f"Sesi admin akan berakhir dalam {timeout_minutes} menit jika tidak ada aktivitas"
    else:
        return f"Sesi user akan berakhir dalam {timeout_minutes} menit jika tidak ada aktivitas"
