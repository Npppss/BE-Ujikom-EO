from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS, ADMIN_SESSION_TIMEOUT_MINUTES, USER_SESSION_TIMEOUT_MINUTES
from typing import Optional

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: timedelta = None, role: str = None):
    """
    Create access token with role-based expiration
    - Admin and user management roles: 5 minutes
    - Regular users: 10 minutes
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    elif role and role in ["admin", "organizer"]:
        # Admin and organizer (user management) get 5 minutes
        expire = datetime.utcnow() + timedelta(minutes=ADMIN_SESSION_TIMEOUT_MINUTES)
    else:
        # Regular users get 10 minutes
        expire = datetime.utcnow() + timedelta(minutes=USER_SESSION_TIMEOUT_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str, token_type: str = "access") -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != token_type:
            return None
        return payload
    except JWTError:
        return None

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_token_expiration_minutes(role: str) -> int:
    """
    Get token expiration time in minutes based on user role
    """
    if role in ["admin", "organizer"]:
        return ADMIN_SESSION_TIMEOUT_MINUTES
    else:
        return USER_SESSION_TIMEOUT_MINUTES
