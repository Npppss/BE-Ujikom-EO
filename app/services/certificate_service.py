from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from app.db.models import Certificate, CertificateTemplate, CertificateVerification, Event, User, Attendance
from app.schemas.certificate import CertificateCreate, CertificateUpdate, CertificateGenerationRequest, BulkCertificateGeneration
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import json
import uuid
import secrets
import os
from PIL import Image, ImageDraw, ImageFont
import io
import base64

class CertificateService:
    def __init__(self):
        self.upload_dir = "uploads/certificates"
        self.template_dir = "uploads/templates"
        self.ensure_directories()
    
    def ensure_directories(self):
        """Ensure upload directories exist"""
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.template_dir, exist_ok=True)
    
    def create_certificate(self, db: Session, certificate_data: CertificateCreate, issued_by: str = None) -> Certificate:
        """Create a new certificate"""
        # Get event and user data
        event = db.query(Event).filter(Event.id == certificate_data.event_id).first()
        user = db.query(User).filter(User.id == certificate_data.user_id).first()
        
        if not event or not user:
            raise Exception("Event or user not found")
        
        # Generate verification code
        verification_code = secrets.token_urlsafe(16)
        
        # Create certificate
        certificate = Certificate(
            title=certificate_data.title,
            description=certificate_data.description,
            certificate_type=certificate_data.certificate_type,
            file_format=certificate_data.file_format,
            participant_name=certificate_data.participant_name,
            event_name=certificate_data.event_name,
            event_date=certificate_data.event_date,
            event_location=certificate_data.event_location,
            achievement_score=certificate_data.achievement_score,
            achievement_level=certificate_data.achievement_level,
            completion_hours=certificate_data.completion_hours,
            event_id=certificate_data.event_id,
            user_id=certificate_data.user_id,
            verification_code=verification_code,
            issued_by=issued_by
        )
        
        # Set template if provided
        if certificate_data.template_id:
            template = db.query(CertificateTemplate).filter(CertificateTemplate.id == certificate_data.template_id).first()
            if template:
                certificate.template_url = template.template_url
        
        db.add(certificate)
        db.commit()
        db.refresh(certificate)
        
        return certificate
    
    def get_certificate(self, db: Session, certificate_id: int) -> Optional[Certificate]:
        """Get certificate by ID"""
        return db.query(Certificate).filter(Certificate.id == certificate_id).first()
    
    def get_certificate_by_code(self, db: Session, certificate_id: str) -> Optional[Certificate]:
        """Get certificate by certificate ID"""
        return db.query(Certificate).filter(Certificate.certificate_id == certificate_id).first()
    
    def get_user_certificates(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Certificate]:
        """Get certificates for a specific user"""
        return db.query(Certificate).filter(
            Certificate.user_id == user_id
        ).offset(skip).limit(limit).all()
    
    def get_event_certificates(self, db: Session, event_id: int, skip: int = 0, limit: int = 100) -> List[Certificate]:
        """Get certificates for a specific event"""
        return db.query(Certificate).filter(
            Certificate.event_id == event_id
        ).offset(skip).limit(limit).all()
    
    def update_certificate(self, db: Session, certificate_id: int, certificate_data: CertificateUpdate) -> Optional[Certificate]:
        """Update certificate"""
        certificate = db.query(Certificate).filter(Certificate.id == certificate_id).first()
        if not certificate:
            return None
        
        # Update fields
        update_data = certificate_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(certificate, field, value)
        
        # Set issued date if being issued
        if update_data.get('is_issued') and not certificate.issued_date:
            certificate.issued_date = datetime.utcnow()
        
        db.commit()
        db.refresh(certificate)
        return certificate
    
    def delete_certificate(self, db: Session, certificate_id: int) -> bool:
        """Delete certificate"""
        certificate = db.query(Certificate).filter(Certificate.id == certificate_id).first()
        if not certificate:
            return False
        
        # Delete generated file if exists
        if certificate.generated_url:
            try:
                file_path = certificate.generated_url.replace("uploads/", "")
                full_path = os.path.join(self.upload_dir, file_path)
                if os.path.exists(full_path):
                    os.remove(full_path)
            except Exception:
                pass  # Ignore file deletion errors
        
        db.delete(certificate)
        db.commit()
        return True
    
    def issue_certificate(self, db: Session, certificate_id: int, issued_by: str) -> Optional[Certificate]:
        """Issue a certificate"""
        certificate = db.query(Certificate).filter(Certificate.id == certificate_id).first()
        if not certificate:
            return None
        
        certificate.is_issued = True
        certificate.issued_date = datetime.utcnow()
        certificate.issued_by = issued_by
        
        db.commit()
        db.refresh(certificate)
        return certificate
    
    def generate_certificate_pdf(self, db: Session, certificate_id: int, template_id: Optional[int] = None) -> str:
        """Generate PDF certificate"""
        certificate = db.query(Certificate).filter(Certificate.id == certificate_id).first()
        if not certificate:
            raise Exception("Certificate not found")
        
        # Get template
        template = None
        if template_id:
            template = db.query(CertificateTemplate).filter(CertificateTemplate.id == template_id).first()
        
        if not template:
            # Use default template
            template = db.query(CertificateTemplate).filter(CertificateTemplate.is_default == True).first()
        
        # Generate certificate using template
        # This is a simplified version - in production you'd use a proper PDF library
        certificate_url = self._create_simple_certificate(certificate, template)
        
        # Update certificate with generated URL
        certificate.generated_url = certificate_url
        db.commit()
        
        return certificate_url
    
    def _create_simple_certificate(self, certificate: Certificate, template: Optional[CertificateTemplate] = None) -> str:
        """Create a simple certificate image (placeholder for PDF generation)"""
        # Create a simple certificate image
        width, height = 800, 600
        img = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(img)
        
        # Add border
        draw.rectangle([(20, 20), (width-20, height-20)], outline='black', width=3)
        
        # Add title
        title_font = ImageFont.load_default()
        draw.text((width//2, 100), "CERTIFICATE OF PARTICIPATION", fill='black', anchor='mm', font=title_font)
        
        # Add participant name
        draw.text((width//2, 200), f"This is to certify that", fill='black', anchor='mm', font=title_font)
        draw.text((width//2, 230), certificate.participant_name, fill='blue', anchor='mm', font=title_font)
        
        # Add event details
        draw.text((width//2, 280), f"has participated in", fill='black', anchor='mm', font=title_font)
        draw.text((width//2, 310), certificate.event_name, fill='black', anchor='mm', font=title_font)
        draw.text((width//2, 340), f"on {certificate.event_date.strftime('%B %d, %Y')}", fill='black', anchor='mm', font=title_font)
        
        # Add certificate ID
        draw.text((width//2, 400), f"Certificate ID: {certificate.certificate_id}", fill='gray', anchor='mm', font=title_font)
        
        # Add verification code
        if certificate.verification_code:
            draw.text((width//2, 430), f"Verification Code: {certificate.verification_code}", fill='gray', anchor='mm', font=title_font)
        
        # Save image
        filename = f"certificate_{certificate.certificate_id}.png"
        filepath = os.path.join(self.upload_dir, filename)
        img.save(filepath)
        
        return f"uploads/certificates/{filename}"
    
    def verify_certificate(self, db: Session, verification_code: str, ip_address: str = None, user_agent: str = None) -> Dict[str, Any]:
        """Verify a certificate"""
        certificate = db.query(Certificate).filter(Certificate.verification_code == verification_code).first()
        
        if not certificate:
            return {
                "is_valid": False,
                "message": "Certificate not found",
                "certificate_data": None
            }
        
        if not certificate.is_valid:
            return {
                "is_valid": False,
                "message": "Certificate is invalid or revoked",
                "certificate_data": certificate
            }
        
        if certificate.expiry_date and certificate.expiry_date < datetime.utcnow():
            return {
                "is_valid": False,
                "message": "Certificate has expired",
                "certificate_data": certificate
            }
        
        # Record verification
        verification = CertificateVerification(
            certificate_id=certificate.id,
            verification_code=verification_code,
            verification_date=datetime.utcnow(),
            ip_address=ip_address,
            user_agent=user_agent,
            is_valid=True
        )
        db.add(verification)
        
        # Mark certificate as verified if not already
        if not certificate.is_verified:
            certificate.is_verified = True
            certificate.verified_at = datetime.utcnow()
        
        db.commit()
        
        return {
            "is_valid": True,
            "message": "Certificate is valid",
            "certificate_data": certificate
        }
    
    def bulk_generate_certificates(self, db: Session, bulk_data: BulkCertificateGeneration, issued_by: str) -> Dict[str, Any]:
        """Generate certificates for all event participants"""
        # Get event
        event = db.query(Event).filter(Event.id == bulk_data.event_id).first()
        if not event:
            raise Exception("Event not found")
        
        # Get all participants (users who attended the event)
        attendances = db.query(Attendance).filter(
            Attendance.event_id == bulk_data.event_id,
            Attendance.check_in_qr_scanned == True
        ).all()
        
        if not attendances:
            raise Exception("No participants found for this event")
        
        certificates_generated = 0
        failed_generations = 0
        certificate_ids = []
        
        for attendance in attendances:
            try:
                # Get user
                user = db.query(User).filter(User.id == attendance.user_id).first()
                if not user:
                    continue
                
                # Check if certificate already exists
                existing_certificate = db.query(Certificate).filter(
                    Certificate.event_id == bulk_data.event_id,
                    Certificate.user_id == user.id
                ).first()
                
                if existing_certificate:
                    continue
                
                # Create certificate
                certificate_data = CertificateCreate(
                    title=bulk_data.title,
                    description=bulk_data.description,
                    certificate_type=bulk_data.certificate_type,
                    file_format=bulk_data.file_format,
                    participant_name=user.full_name or user.email,
                    event_name=event.title,
                    event_date=event.start_date,
                    event_location=event.location,
                    achievement_score=bulk_data.achievement_score,
                    achievement_level=bulk_data.achievement_level,
                    completion_hours=bulk_data.completion_hours,
                    event_id=bulk_data.event_id,
                    user_id=user.id,
                    template_id=bulk_data.template_id
                )
                
                certificate = self.create_certificate(db, certificate_data, issued_by)
                
                # Issue certificate
                self.issue_certificate(db, certificate.id, issued_by)
                
                # Generate PDF
                self.generate_certificate_pdf(db, certificate.id, bulk_data.template_id)
                
                certificates_generated += 1
                certificate_ids.append(certificate.certificate_id)
                
            except Exception as e:
                failed_generations += 1
                print(f"Failed to generate certificate for user {attendance.user_id}: {str(e)}")
        
        return {
            "total_participants": len(attendances),
            "certificates_generated": certificates_generated,
            "failed_generations": failed_generations,
            "certificate_ids": certificate_ids
        }
    
    def get_certificate_stats(self, db: Session, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Get certificate statistics"""
        query = db.query(Certificate)
        
        if user_id:
            query = query.filter(Certificate.user_id == user_id)
        
        certificates = query.all()
        
        # Basic stats
        total_certificates = len(certificates)
        issued_certificates = len([c for c in certificates if c.is_issued])
        valid_certificates = len([c for c in certificates if c.is_valid])
        verified_certificates = len([c for c in certificates if c.is_verified])
        
        # Certificates by type
        certificates_by_type = {}
        for cert in certificates:
            cert_type = cert.certificate_type
            certificates_by_type[cert_type] = certificates_by_type.get(cert_type, 0) + 1
        
        # Certificates by month (last 12 months)
        certificates_by_month = []
        for i in range(12):
            month_date = datetime.utcnow() - timedelta(days=30*i)
            month_certs = [c for c in certificates if c.created_at.month == month_date.month and c.created_at.year == month_date.year]
            certificates_by_month.append({
                "month": month_date.strftime("%Y-%m"),
                "count": len(month_certs)
            })
        
        # Top events by certificate count
        event_cert_counts = {}
        for cert in certificates:
            event_name = cert.event_name
            event_cert_counts[event_name] = event_cert_counts.get(event_name, 0) + 1
        
        top_events = sorted(event_cert_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        top_events = [{"event_name": name, "certificate_count": count} for name, count in top_events]
        
        return {
            "total_certificates": total_certificates,
            "issued_certificates": issued_certificates,
            "valid_certificates": valid_certificates,
            "verified_certificates": verified_certificates,
            "certificates_by_type": certificates_by_type,
            "certificates_by_month": certificates_by_month,
            "top_events": top_events
        }
    
    def upload_template(self, file_content: bytes, filename: str) -> str:
        """Upload certificate template"""
        # Validate file type
        allowed_extensions = ['.pdf', '.png', '.jpg', '.jpeg']
        file_ext = os.path.splitext(filename)[1].lower()
        
        if file_ext not in allowed_extensions:
            raise Exception("Invalid file type. Allowed: PDF, PNG, JPG")
        
        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        filepath = os.path.join(self.template_dir, unique_filename)
        
        # Save file
        with open(filepath, 'wb') as f:
            f.write(file_content)
        
        return f"uploads/templates/{unique_filename}"

# Create service instance
certificate_service = CertificateService() 