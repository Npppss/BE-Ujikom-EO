from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import uuid

def generate_certificate_id():
    return str(uuid.uuid4())[:8].upper()

class Certificate(Base):
    __tablename__ = "certificates"
    
    id = Column(Integer, primary_key=True, index=True)
    certificate_id = Column(String(20), unique=True, index=True, default=generate_certificate_id)
    
    # Event and User relationship
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    template_id = Column(Integer, ForeignKey("certificate_templates.id"), nullable=True)
    
    # Certificate details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    certificate_type = Column(String(50), default="participation")  # participation, achievement, completion
    
    # File management
    template_url = Column(String(500), nullable=True)  # Template file URL
    generated_url = Column(String(500), nullable=True)  # Generated certificate URL
    file_format = Column(String(10), default="pdf")  # pdf, png, jpg
    
    # Certificate data
    participant_name = Column(String(255), nullable=False)
    event_name = Column(String(255), nullable=False)
    event_date = Column(DateTime, nullable=False)
    event_location = Column(String(255), nullable=True)
    
    # Achievement details
    achievement_score = Column(Float, nullable=True)  # For achievement certificates
    achievement_level = Column(String(50), nullable=True)  # beginner, intermediate, advanced
    completion_hours = Column(Float, nullable=True)  # Hours of participation
    
    # Status and validation
    is_issued = Column(Boolean, default=False)
    issued_date = Column(DateTime, nullable=True)
    issued_by = Column(String(255), nullable=True)
    is_valid = Column(Boolean, default=True)
    expiry_date = Column(DateTime, nullable=True)
    
    # Verification
    verification_code = Column(String(100), unique=True, nullable=True)
    is_verified = Column(Boolean, default=False)
    verified_at = Column(DateTime, nullable=True)
    verified_by = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    event = relationship("Event", back_populates="certificates")
    user = relationship("User", back_populates="certificates")
    template = relationship("CertificateTemplate", back_populates="certificates")
    verifications = relationship("CertificateVerification", back_populates="certificate")

class CertificateTemplate(Base):
    __tablename__ = "certificate_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Template file
    template_url = Column(String(500), nullable=False)
    thumbnail_url = Column(String(500), nullable=True)
    
    # Template configuration
    template_type = Column(String(50), default="default")  # default, custom, premium
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    
    # Design settings (JSON)
    design_config = Column(Text, nullable=True)  # JSON string with design settings
    
    # Usage stats
    usage_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    certificates = relationship("Certificate", back_populates="template")

class CertificateVerification(Base):
    __tablename__ = "certificate_verifications"
    
    id = Column(Integer, primary_key=True, index=True)
    certificate_id = Column(Integer, ForeignKey("certificates.id"), nullable=False)
    
    # Verification details
    verification_code = Column(String(100), nullable=False)
    verification_date = Column(DateTime, nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Verification result
    is_valid = Column(Boolean, default=True)
    verification_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    certificate = relationship("Certificate", back_populates="verifications")
