from sqlalchemy.orm import Session
from app.db.models import User, Role, RefreshToken, PasswordResetToken
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token, verify_token
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
from app.services.email_service import email_service
from datetime import datetime, timedelta
import json
import secrets
from typing import Optional, List

class AuthService:
    def __init__(self):
        pass

    def register_user(self, db: Session, email: str, password: str, full_name: str = None) -> User:
        """Register a new user with email verification"""
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            raise Exception("User with this email already exists")
        
        # Get default role (user role)
        default_role = db.query(Role).filter(Role.name == "user").first()
        if not default_role:
            # Create default roles if they don't exist
            self._create_default_roles(db)
            default_role = db.query(Role).filter(Role.name == "user").first()
        
        # Generate email verification token
        verification_token = secrets.token_urlsafe(32)
        verification_expires = datetime.utcnow() + timedelta(hours=24)
        
        # Create new user (not verified initially)
        hashed_password = get_password_hash(password)
        new_user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            role_id=default_role.id,
            is_verified=False,  # User needs to verify email first
            email_verification_token=verification_token,
            email_verification_expires=verification_expires
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Send email verification
        try:
            email_service.send_email_verification(email, verification_token, full_name)
        except Exception as e:
            # Log error but don't fail registration
            print(f"Failed to send email verification: {e}")
        
        return new_user

    def verify_email(self, db: Session, token: str) -> bool:
        """Verify user email with token"""
        # Find user with this verification token
        user = db.query(User).filter(
            User.email_verification_token == token,
            User.email_verification_expires > datetime.utcnow(),
            User.is_verified == False
        ).first()
        
        if not user:
            raise Exception("Invalid or expired verification token")
        
        # Mark user as verified
        user.is_verified = True
        user.email_verification_token = None
        user.email_verification_expires = None
        
        db.commit()
        
        # Send welcome email after verification
        try:
            email_service.send_welcome_email(user.email, user.full_name)
        except Exception as e:
            print(f"Failed to send welcome email: {e}")
        
        return True

    def resend_verification_email(self, db: Session, email: str) -> bool:
        """Resend email verification"""
        user = db.query(User).filter(User.email == email).first()
        if not user:
            # Don't reveal if user exists or not for security
            return True
        
        if user.is_verified:
            raise Exception("Email is already verified")
        
        # Generate new verification token
        verification_token = secrets.token_urlsafe(32)
        verification_expires = datetime.utcnow() + timedelta(hours=24)
        
        # Update user with new token
        user.email_verification_token = verification_token
        user.email_verification_expires = verification_expires
        
        db.commit()
        
        # Send verification email
        return email_service.send_email_verification(email, verification_token, user.full_name)

    def authenticate_user(self, db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            raise Exception("User account is deactivated")
        if not user.is_verified:
            raise Exception("Please verify your email before logging in")
        return user

    def login_user(self, db: Session, user: User) -> dict:
        """Login user and return tokens"""
        # Create access token
        access_token = create_access_token(
            data={"sub": user.email, "role": user.role.name, "user_id": user.id}
        )
        
        # Create refresh token
        refresh_token = create_refresh_token(
            data={"sub": user.email, "user_id": user.id}
        )
        
        # Store refresh token in database
        refresh_token_db = RefreshToken(
            token=refresh_token,
            user_id=user.id,
            expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        )
        db.add(refresh_token_db)
        db.commit()
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }

    def refresh_access_token(self, db: Session, refresh_token: str) -> dict:
        """Refresh access token using refresh token"""
        # Verify refresh token
        payload = verify_token(refresh_token, "refresh")
        if not payload:
            raise Exception("Invalid refresh token")
        
        # Check if refresh token exists in database and is not revoked
        token_db = db.query(RefreshToken).filter(
            RefreshToken.token == refresh_token,
            RefreshToken.is_revoked == False,
            RefreshToken.expires_at > datetime.utcnow()
        ).first()
        
        if not token_db:
            raise Exception("Refresh token not found or expired")
        
        # Get user
        user = db.query(User).filter(User.id == payload.get("user_id")).first()
        if not user or not user.is_active:
            raise Exception("User not found or inactive")
        
        # Create new access token
        new_access_token = create_access_token(
            data={"sub": user.email, "role": user.role.name, "user_id": user.id}
        )
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }

    def logout_user(self, db: Session, refresh_token: str) -> bool:
        """Logout user by revoking refresh token"""
        token_db = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()
        if token_db:
            token_db.is_revoked = True
            db.commit()
            return True
        return False

    def forgot_password(self, db: Session, email: str) -> bool:
        """Send password reset email"""
        user = db.query(User).filter(User.email == email).first()
        if not user:
            # Don't reveal if user exists or not for security
            return True
        
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        
        # Store reset token in database
        reset_token_db = PasswordResetToken(
            token=reset_token,
            user_id=user.id,
            expires_at=datetime.utcnow() + timedelta(hours=1)  # 1 hour expiry
        )
        db.add(reset_token_db)
        db.commit()
        
        # Send email
        return email_service.send_password_reset_email(email, reset_token, user.full_name)

    def reset_password(self, db: Session, token: str, new_password: str) -> bool:
        """Reset password using reset token"""
        # Find valid reset token
        reset_token_db = db.query(PasswordResetToken).filter(
            PasswordResetToken.token == token,
            PasswordResetToken.is_used == False,
            PasswordResetToken.expires_at > datetime.utcnow()
        ).first()
        
        if not reset_token_db:
            raise Exception("Invalid or expired reset token")
        
        # Get user
        user = db.query(User).filter(User.id == reset_token_db.user_id).first()
        if not user:
            raise Exception("User not found")
        
        # Update password
        user.hashed_password = get_password_hash(new_password)
        
        # Mark token as used
        reset_token_db.is_used = True
        
        # Revoke all refresh tokens for this user
        db.query(RefreshToken).filter(RefreshToken.user_id == user.id).update({"is_revoked": True})
        
        db.commit()
        return True

    def change_password(self, db: Session, user: User, current_password: str, new_password: str) -> bool:
        """Change password for authenticated user"""
        if not verify_password(current_password, user.hashed_password):
            raise Exception("Current password is incorrect")
        
        user.hashed_password = get_password_hash(new_password)
        
        # Revoke all refresh tokens for this user
        db.query(RefreshToken).filter(RefreshToken.user_id == user.id).update({"is_revoked": True})
        
        db.commit()
        return True

    def get_current_user(self, db: Session, token: str) -> Optional[User]:
        """Get current user from access token"""
        payload = verify_token(token, "access")
        if not payload:
            return None
        
        user = db.query(User).filter(User.id == payload.get("user_id")).first()
        if not user or not user.is_active:
            return None
        
        return user

    def check_permission(self, user: User, required_permission: str) -> bool:
        """Check if user has required permission"""
        if not user.role or not user.role.permissions:
            return False
        
        try:
            permissions = json.loads(user.role.permissions)
            return required_permission in permissions
        except (json.JSONDecodeError, TypeError):
            return False

    def _create_default_roles(self, db: Session):
        """Create default roles if they don't exist"""
        default_roles = [
            {
                "name": "admin",
                "description": "Administrator with full access",
                "permissions": [
                    "user:read", "user:create", "user:update", "user:delete",
                    "role:read", "role:create", "role:update", "role:delete",
                    "event:read", "event:create", "event:update", "event:delete"
                ]
            },
            {
                "name": "organizer",
                "description": "Event organizer with event management access",
                "permissions": [
                    "event:read", "event:create", "event:update", "event:delete",
                    "user:read"
                ]
            },
            {
                "name": "user",
                "description": "Regular user with basic access",
                "permissions": [
                    "event:read"
                ]
            }
        ]
        
        for role_data in default_roles:
            existing_role = db.query(Role).filter(Role.name == role_data["name"]).first()
            if not existing_role:
                new_role = Role(
                    name=role_data["name"],
                    description=role_data["description"],
                    permissions=json.dumps(role_data["permissions"])
                )
                db.add(new_role)
        
        db.commit()

# Create service instance
auth_service = AuthService()
