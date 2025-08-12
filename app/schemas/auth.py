from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from app.core.password_validator import password_validator

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    
    @validator('password')
    def validate_password_strength(cls, v):
        """Validasi password strength menggunakan regex"""
        is_valid, errors = password_validator.validate_password(v)
        if not is_valid:
            raise ValueError(f"Password tidak memenuhi requirement: {'; '.join(errors)}")
        
        # Cek apakah password termasuk password umum
        if password_validator.is_common_password(v):
            raise ValueError("Password terlalu umum dan mudah ditebak. Gunakan password yang lebih unik.")
        
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    email: str | None = None
    role: str | None = None

class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password_strength(cls, v):
        """Validasi password strength untuk reset password"""
        is_valid, errors = password_validator.validate_password(v)
        if not is_valid:
            raise ValueError(f"Password tidak memenuhi requirement: {'; '.join(errors)}")
        
        # Cek apakah password termasuk password umum
        if password_validator.is_common_password(v):
            raise ValueError("Password terlalu umum dan mudah ditebak. Gunakan password yang lebih unik.")
        
        return v

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_new_password_strength(cls, v):
        """Validasi password strength untuk change password"""
        is_valid, errors = password_validator.validate_password(v)
        if not is_valid:
            raise ValueError(f"Password tidak memenuhi requirement: {'; '.join(errors)}")
        
        # Cek apakah password termasuk password umum
        if password_validator.is_common_password(v):
            raise ValueError("Password terlalu umum dan mudah ditebak. Gunakan password yang lebih unik.")
        
        return v

class EmailVerificationRequest(BaseModel):
    token: str

class ResendVerificationRequest(BaseModel):
    email: EmailStr

class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    permissions: List[str] = []

class RoleOut(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    permissions: List[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role_id: Optional[int] = None
    is_active: Optional[bool] = None

class PasswordRequirementsResponse(BaseModel):
    """Response untuk menampilkan requirement password"""
    min_length: int
    requirements: List[str]
    example: str
