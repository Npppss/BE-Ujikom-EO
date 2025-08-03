from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum

class CertificateType(str, Enum):
    PARTICIPATION = "participation"
    ACHIEVEMENT = "achievement"
    COMPLETION = "completion"

class AchievementLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class FileFormat(str, Enum):
    PDF = "pdf"
    PNG = "png"
    JPG = "jpg"

# Certificate Schemas
class CertificateBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    certificate_type: CertificateType = CertificateType.PARTICIPATION
    file_format: FileFormat = FileFormat.PDF
    
    # Certificate data
    participant_name: str = Field(..., min_length=1, max_length=255)
    event_name: str = Field(..., min_length=1, max_length=255)
    event_date: datetime
    event_location: Optional[str] = Field(None, max_length=255)
    
    # Achievement details
    achievement_score: Optional[float] = Field(None, ge=0, le=100)
    achievement_level: Optional[AchievementLevel] = None
    completion_hours: Optional[float] = Field(None, ge=0)

class CertificateCreate(CertificateBase):
    event_id: int
    user_id: int
    template_id: Optional[int] = None

class CertificateUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    certificate_type: Optional[CertificateType] = None
    file_format: Optional[FileFormat] = None
    
    # Certificate data
    participant_name: Optional[str] = Field(None, min_length=1, max_length=255)
    event_name: Optional[str] = Field(None, min_length=1, max_length=255)
    event_date: Optional[datetime] = None
    event_location: Optional[str] = Field(None, max_length=255)
    
    # Achievement details
    achievement_score: Optional[float] = Field(None, ge=0, le=100)
    achievement_level: Optional[AchievementLevel] = None
    completion_hours: Optional[float] = Field(None, ge=0)
    
    # Status
    is_issued: Optional[bool] = None
    issued_by: Optional[str] = Field(None, max_length=255)
    is_valid: Optional[bool] = None
    expiry_date: Optional[datetime] = None

class CertificateOut(CertificateBase):
    id: int
    certificate_id: str
    event_id: int
    user_id: int
    user_name: str
    user_email: str
    
    # File management
    template_url: Optional[str] = None
    generated_url: Optional[str] = None
    
    # Status and validation
    is_issued: bool
    issued_date: Optional[datetime] = None
    issued_by: Optional[str] = None
    is_valid: bool
    expiry_date: Optional[datetime] = None
    
    # Verification
    verification_code: Optional[str] = None
    is_verified: bool
    verified_at: Optional[datetime] = None
    verified_by: Optional[str] = None
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class CertificateList(BaseModel):
    id: int
    certificate_id: str
    title: str
    certificate_type: CertificateType
    participant_name: str
    event_name: str
    event_date: datetime
    is_issued: bool
    is_valid: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Certificate Template Schemas
class CertificateTemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    template_url: str = Field(..., min_length=1, max_length=500)
    thumbnail_url: Optional[str] = Field(None, max_length=500)
    template_type: str = Field("default", max_length=50)
    is_active: bool = True
    is_default: bool = False
    design_config: Optional[str] = None  # JSON string

class CertificateTemplateCreate(CertificateTemplateBase):
    pass

class CertificateTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    template_url: Optional[str] = Field(None, min_length=1, max_length=500)
    thumbnail_url: Optional[str] = Field(None, max_length=500)
    template_type: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None
    design_config: Optional[str] = None

class CertificateTemplateOut(CertificateTemplateBase):
    id: int
    usage_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Certificate Generation Schemas
class CertificateGenerationRequest(BaseModel):
    certificate_id: int
    template_id: Optional[int] = None
    custom_data: Optional[dict] = None  # Additional data for certificate

class CertificateGenerationResponse(BaseModel):
    certificate_id: int
    generated_url: str
    download_url: str
    message: str

# Certificate Verification Schemas
class CertificateVerificationRequest(BaseModel):
    verification_code: str = Field(..., min_length=1, max_length=100)

class CertificateVerificationResponse(BaseModel):
    certificate_id: str
    is_valid: bool
    certificate_data: Optional[CertificateOut] = None
    verification_notes: Optional[str] = None
    message: str

# Bulk Certificate Generation
class BulkCertificateGeneration(BaseModel):
    event_id: int
    template_id: Optional[int] = None
    certificate_type: CertificateType = CertificateType.PARTICIPATION
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    file_format: FileFormat = FileFormat.PDF
    achievement_score: Optional[float] = Field(None, ge=0, le=100)
    achievement_level: Optional[AchievementLevel] = None
    completion_hours: Optional[float] = Field(None, ge=0)
    issued_by: Optional[str] = Field(None, max_length=255)

class BulkCertificateResponse(BaseModel):
    total_participants: int
    certificates_generated: int
    failed_generations: int
    message: str
    certificate_ids: List[str]

# Certificate Statistics
class CertificateStats(BaseModel):
    total_certificates: int
    issued_certificates: int
    valid_certificates: int
    verified_certificates: int
    certificates_by_type: dict
    certificates_by_month: List[dict]
    top_events: List[dict]

# File Upload Schemas
class FileUploadResponse(BaseModel):
    file_url: str
    file_name: str
    file_size: int
    file_type: str
    message: str 