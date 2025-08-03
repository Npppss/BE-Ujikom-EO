from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.auth import (
    UserCreate, UserLogin, Token, UserOut, RefreshTokenRequest,
    ForgotPasswordRequest, ResetPasswordRequest, ChangePasswordRequest,
    EmailVerificationRequest, ResendVerificationRequest
)
from app.services.auth_service import auth_service
from app.core.dependencies import get_current_active_user
from app.db.models import User

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user with email verification"""
    try:
        new_user = auth_service.register_user(
            db, 
            user.email, 
            user.password, 
            user.full_name
        )
        return UserOut(
            id=new_user.id,
            email=new_user.email,
            full_name=new_user.full_name,
            role=new_user.role.name,
            is_active=new_user.is_active,
            is_verified=new_user.is_verified,
            created_at=new_user.created_at
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/verify-email")
def verify_email(request: EmailVerificationRequest, db: Session = Depends(get_db)):
    """Verify user email with token"""
    try:
        success = auth_service.verify_email(db, request.token)
        if success:
            return {"message": "Email verified successfully. You can now log in."}
        else:
            raise HTTPException(status_code=400, detail="Failed to verify email")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/resend-verification")
def resend_verification(request: ResendVerificationRequest, db: Session = Depends(get_db)):
    """Resend email verification"""
    try:
        success = auth_service.resend_verification_email(db, request.email)
        if success:
            return {"message": "Verification email sent successfully"}
        else:
            raise HTTPException(status_code=400, detail="Failed to send verification email")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    """Login user and get access token"""
    try:
        auth_user = auth_service.authenticate_user(db, user.email, user.password)
        if not auth_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        tokens = auth_service.login_user(db, auth_user)
        return tokens
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/refresh", response_model=Token)
def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Refresh access token using refresh token"""
    try:
        tokens = auth_service.refresh_access_token(db, request.refresh_token)
        return tokens
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/logout")
def logout(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Logout user by revoking refresh token"""
    try:
        success = auth_service.logout_user(db, request.refresh_token)
        if success:
            return {"message": "Successfully logged out"}
        else:
            raise HTTPException(status_code=400, detail="Invalid refresh token")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Send password reset email"""
    try:
        success = auth_service.forgot_password(db, request.email)
        return {"message": "If the email exists, a password reset link has been sent"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Reset password using reset token"""
    try:
        success = auth_service.reset_password(db, request.token, request.new_password)
        if success:
            return {"message": "Password has been reset successfully"}
        else:
            raise HTTPException(status_code=400, detail="Failed to reset password")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/change-password")
def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Change password for authenticated user"""
    try:
        success = auth_service.change_password(
            db, 
            current_user, 
            request.current_password, 
            request.new_password
        )
        if success:
            return {"message": "Password changed successfully"}
        else:
            raise HTTPException(status_code=400, detail="Failed to change password")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/me", response_model=UserOut)
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return UserOut(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role.name,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at
    )
