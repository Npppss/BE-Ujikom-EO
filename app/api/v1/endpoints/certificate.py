from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.schemas.certificate import (
    CertificateCreate, CertificateUpdate, CertificateOut, CertificateList,
    CertificateTemplateCreate, CertificateTemplateUpdate, CertificateTemplateOut,
    CertificateGenerationRequest, CertificateGenerationResponse,
    CertificateVerificationRequest, CertificateVerificationResponse,
    BulkCertificateGeneration, BulkCertificateResponse, CertificateStats,
    FileUploadResponse
)
from app.services.certificate_service import certificate_service
from app.core.dependencies import get_current_active_user, require_permission
from app.db.models import User, Certificate, CertificateTemplate

router = APIRouter(prefix="/certificates", tags=["Certificate Management"])

# Certificate CRUD Operations

@router.post("/", response_model=CertificateOut)
def create_certificate(
    certificate: CertificateCreate,
    current_user: User = Depends(require_permission("certificate:create")),
    db: Session = Depends(get_db)
):
    """Create a new certificate"""
    try:
        new_certificate = certificate_service.create_certificate(
            db, certificate, current_user.full_name or current_user.email
        )
        
        # Get user data for response
        user = db.query(User).filter(User.id == new_certificate.user_id).first()
        
        return CertificateOut(
            id=new_certificate.id,
            certificate_id=new_certificate.certificate_id,
            title=new_certificate.title,
            description=new_certificate.description,
            certificate_type=new_certificate.certificate_type,
            file_format=new_certificate.file_format,
            participant_name=new_certificate.participant_name,
            event_name=new_certificate.event_name,
            event_date=new_certificate.event_date,
            event_location=new_certificate.event_location,
            achievement_score=new_certificate.achievement_score,
            achievement_level=new_certificate.achievement_level,
            completion_hours=new_certificate.completion_hours,
            event_id=new_certificate.event_id,
            user_id=new_certificate.user_id,
            user_name=user.full_name if user else "Unknown",
            user_email=user.email if user else "Unknown",
            template_url=new_certificate.template_url,
            generated_url=new_certificate.generated_url,
            is_issued=new_certificate.is_issued,
            issued_date=new_certificate.issued_date,
            issued_by=new_certificate.issued_by,
            is_valid=new_certificate.is_valid,
            expiry_date=new_certificate.expiry_date,
            verification_code=new_certificate.verification_code,
            is_verified=new_certificate.is_verified,
            verified_at=new_certificate.verified_at,
            verified_by=new_certificate.verified_by,
            created_at=new_certificate.created_at,
            updated_at=new_certificate.updated_at
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[CertificateList])
def get_certificates(
    event_id: Optional[int] = Query(None, description="Filter by event ID"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    certificate_type: Optional[str] = Query(None, description="Filter by certificate type"),
    is_issued: Optional[bool] = Query(None, description="Filter by issued status"),
    skip: int = Query(0, ge=0, description="Skip records"),
    limit: int = Query(100, ge=1, le=1000, description="Limit records"),
    current_user: User = Depends(require_permission("certificate:read")),
    db: Session = Depends(get_db)
):
    """Get certificates with filtering"""
    try:
        query = db.query(Certificate)
        
        # Apply filters
        if event_id:
            query = query.filter(Certificate.event_id == event_id)
        if user_id:
            query = query.filter(Certificate.user_id == user_id)
        if certificate_type:
            query = query.filter(Certificate.certificate_type == certificate_type)
        if is_issued is not None:
            query = query.filter(Certificate.is_issued == is_issued)
        
        # Get certificates
        certificates = query.offset(skip).limit(limit).all()
        
        # Convert to response format
        result = []
        for cert in certificates:
            result.append(CertificateList(
                id=cert.id,
                certificate_id=cert.certificate_id,
                title=cert.title,
                certificate_type=cert.certificate_type,
                participant_name=cert.participant_name,
                event_name=cert.event_name,
                event_date=cert.event_date,
                is_issued=cert.is_issued,
                is_valid=cert.is_valid,
                created_at=cert.created_at
            ))
        
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{certificate_id}", response_model=CertificateOut)
def get_certificate(
    certificate_id: int,
    current_user: User = Depends(require_permission("certificate:read")),
    db: Session = Depends(get_db)
):
    """Get certificate by ID"""
    try:
        certificate = certificate_service.get_certificate(db, certificate_id)
        if not certificate:
            raise HTTPException(status_code=404, detail="Certificate not found")
        
        # Get user data
        user = db.query(User).filter(User.id == certificate.user_id).first()
        
        return CertificateOut(
            id=certificate.id,
            certificate_id=certificate.certificate_id,
            title=certificate.title,
            description=certificate.description,
            certificate_type=certificate.certificate_type,
            file_format=certificate.file_format,
            participant_name=certificate.participant_name,
            event_name=certificate.event_name,
            event_date=certificate.event_date,
            event_location=certificate.event_location,
            achievement_score=certificate.achievement_score,
            achievement_level=certificate.achievement_level,
            completion_hours=certificate.completion_hours,
            event_id=certificate.event_id,
            user_id=certificate.user_id,
            user_name=user.full_name if user else "Unknown",
            user_email=user.email if user else "Unknown",
            template_url=certificate.template_url,
            generated_url=certificate.generated_url,
            is_issued=certificate.is_issued,
            issued_date=certificate.issued_date,
            issued_by=certificate.issued_by,
            is_valid=certificate.is_valid,
            expiry_date=certificate.expiry_date,
            verification_code=certificate.verification_code,
            is_verified=certificate.is_verified,
            verified_at=certificate.verified_at,
            verified_by=certificate.verified_by,
            created_at=certificate.created_at,
            updated_at=certificate.updated_at
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{certificate_id}", response_model=CertificateOut)
def update_certificate(
    certificate_id: int,
    certificate: CertificateUpdate,
    current_user: User = Depends(require_permission("certificate:update")),
    db: Session = Depends(get_db)
):
    """Update certificate"""
    try:
        updated_certificate = certificate_service.update_certificate(db, certificate_id, certificate)
        if not updated_certificate:
            raise HTTPException(status_code=404, detail="Certificate not found")
        
        # Get user data
        user = db.query(User).filter(User.id == updated_certificate.user_id).first()
        
        return CertificateOut(
            id=updated_certificate.id,
            certificate_id=updated_certificate.certificate_id,
            title=updated_certificate.title,
            description=updated_certificate.description,
            certificate_type=updated_certificate.certificate_type,
            file_format=updated_certificate.file_format,
            participant_name=updated_certificate.participant_name,
            event_name=updated_certificate.event_name,
            event_date=updated_certificate.event_date,
            event_location=updated_certificate.event_location,
            achievement_score=updated_certificate.achievement_score,
            achievement_level=updated_certificate.achievement_level,
            completion_hours=updated_certificate.completion_hours,
            event_id=updated_certificate.event_id,
            user_id=updated_certificate.user_id,
            user_name=user.full_name if user else "Unknown",
            user_email=user.email if user else "Unknown",
            template_url=updated_certificate.template_url,
            generated_url=updated_certificate.generated_url,
            is_issued=updated_certificate.is_issued,
            issued_date=updated_certificate.issued_date,
            issued_by=updated_certificate.issued_by,
            is_valid=updated_certificate.is_valid,
            expiry_date=updated_certificate.expiry_date,
            verification_code=updated_certificate.verification_code,
            is_verified=updated_certificate.is_verified,
            verified_at=updated_certificate.verified_at,
            verified_by=updated_certificate.verified_by,
            created_at=updated_certificate.created_at,
            updated_at=updated_certificate.updated_at
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{certificate_id}")
def delete_certificate(
    certificate_id: int,
    current_user: User = Depends(require_permission("certificate:delete")),
    db: Session = Depends(get_db)
):
    """Delete certificate"""
    try:
        success = certificate_service.delete_certificate(db, certificate_id)
        if not success:
            raise HTTPException(status_code=404, detail="Certificate not found")
        
        return {"message": "Certificate deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Certificate Generation and Issuance

@router.post("/{certificate_id}/issue")
def issue_certificate(
    certificate_id: int,
    current_user: User = Depends(require_permission("certificate:update")),
    db: Session = Depends(get_db)
):
    """Issue a certificate"""
    try:
        issued_certificate = certificate_service.issue_certificate(
            db, certificate_id, current_user.full_name or current_user.email
        )
        if not issued_certificate:
            raise HTTPException(status_code=404, detail="Certificate not found")
        
        return {"message": "Certificate issued successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{certificate_id}/generate", response_model=CertificateGenerationResponse)
def generate_certificate(
    certificate_id: int,
    generation_request: CertificateGenerationRequest,
    current_user: User = Depends(require_permission("certificate:update")),
    db: Session = Depends(get_db)
):
    """Generate certificate PDF/image"""
    try:
        generated_url = certificate_service.generate_certificate_pdf(
            db, certificate_id, generation_request.template_id
        )
        
        return CertificateGenerationResponse(
            certificate_id=certificate_id,
            generated_url=generated_url,
            download_url=f"/api/v1/certificates/{certificate_id}/download",
            message="Certificate generated successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/bulk-generate", response_model=BulkCertificateResponse)
def bulk_generate_certificates(
    bulk_data: BulkCertificateGeneration,
    current_user: User = Depends(require_permission("certificate:create")),
    db: Session = Depends(get_db)
):
    """Generate certificates for all event participants"""
    try:
        result = certificate_service.bulk_generate_certificates(
            db, bulk_data, current_user.full_name or current_user.email
        )
        
        return BulkCertificateResponse(
            total_participants=result["total_participants"],
            certificates_generated=result["certificates_generated"],
            failed_generations=result["failed_generations"],
            message=f"Generated {result['certificates_generated']} certificates successfully",
            certificate_ids=result["certificate_ids"]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Certificate Verification

@router.post("/verify", response_model=CertificateVerificationResponse)
def verify_certificate(
    verification_request: CertificateVerificationRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Verify a certificate by verification code"""
    try:
        # Get client IP and user agent
        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        result = certificate_service.verify_certificate(
            db, verification_request.verification_code, client_ip, user_agent
        )
        
        if result["is_valid"] and result["certificate_data"]:
            # Get user data
            user = db.query(User).filter(User.id == result["certificate_data"].user_id).first()
            
            certificate_out = CertificateOut(
                id=result["certificate_data"].id,
                certificate_id=result["certificate_data"].certificate_id,
                title=result["certificate_data"].title,
                description=result["certificate_data"].description,
                certificate_type=result["certificate_data"].certificate_type,
                file_format=result["certificate_data"].file_format,
                participant_name=result["certificate_data"].participant_name,
                event_name=result["certificate_data"].event_name,
                event_date=result["certificate_data"].event_date,
                event_location=result["certificate_data"].event_location,
                achievement_score=result["certificate_data"].achievement_score,
                achievement_level=result["certificate_data"].achievement_level,
                completion_hours=result["certificate_data"].completion_hours,
                event_id=result["certificate_data"].event_id,
                user_id=result["certificate_data"].user_id,
                user_name=user.full_name if user else "Unknown",
                user_email=user.email if user else "Unknown",
                template_url=result["certificate_data"].template_url,
                generated_url=result["certificate_data"].generated_url,
                is_issued=result["certificate_data"].is_issued,
                issued_date=result["certificate_data"].issued_date,
                issued_by=result["certificate_data"].issued_by,
                is_valid=result["certificate_data"].is_valid,
                expiry_date=result["certificate_data"].expiry_date,
                verification_code=result["certificate_data"].verification_code,
                is_verified=result["certificate_data"].is_verified,
                verified_at=result["certificate_data"].verified_at,
                verified_by=result["certificate_data"].verified_by,
                created_at=result["certificate_data"].created_at,
                updated_at=result["certificate_data"].updated_at
            )
        else:
            certificate_out = None
        
        return CertificateVerificationResponse(
            certificate_id=result["certificate_data"].certificate_id if result["certificate_data"] else "",
            is_valid=result["is_valid"],
            certificate_data=certificate_out,
            verification_notes=result.get("verification_notes"),
            message=result["message"]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Certificate Templates

@router.post("/templates/", response_model=CertificateTemplateOut)
def create_template(
    template: CertificateTemplateCreate,
    current_user: User = Depends(require_permission("certificate:create")),
    db: Session = Depends(get_db)
):
    """Create a new certificate template"""
    try:
        new_template = CertificateTemplate(
            name=template.name,
            description=template.description,
            template_url=template.template_url,
            thumbnail_url=template.thumbnail_url,
            template_type=template.template_type,
            is_active=template.is_active,
            is_default=template.is_default,
            design_config=template.design_config
        )
        
        db.add(new_template)
        db.commit()
        db.refresh(new_template)
        
        return CertificateTemplateOut(
            id=new_template.id,
            name=new_template.name,
            description=new_template.description,
            template_url=new_template.template_url,
            thumbnail_url=new_template.thumbnail_url,
            template_type=new_template.template_type,
            is_active=new_template.is_active,
            is_default=new_template.is_default,
            design_config=new_template.design_config,
            usage_count=new_template.usage_count,
            created_at=new_template.created_at,
            updated_at=new_template.updated_at
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/templates/", response_model=List[CertificateTemplateOut])
def get_templates(
    template_type: Optional[str] = Query(None, description="Filter by template type"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    current_user: User = Depends(require_permission("certificate:read")),
    db: Session = Depends(get_db)
):
    """Get certificate templates"""
    try:
        query = db.query(CertificateTemplate)
        
        if template_type:
            query = query.filter(CertificateTemplate.template_type == template_type)
        if is_active is not None:
            query = query.filter(CertificateTemplate.is_active == is_active)
        
        templates = query.all()
        
        result = []
        for template in templates:
            result.append(CertificateTemplateOut(
                id=template.id,
                name=template.name,
                description=template.description,
                template_url=template.template_url,
                thumbnail_url=template.thumbnail_url,
                template_type=template.template_type,
                is_active=template.is_active,
                is_default=template.is_default,
                design_config=template.design_config,
                usage_count=template.usage_count,
                created_at=template.created_at,
                updated_at=template.updated_at
            ))
        
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# File Upload

@router.post("/upload-template", response_model=FileUploadResponse)
def upload_template(
    file: UploadFile = File(...),
    current_user: User = Depends(require_permission("certificate:create")),
    db: Session = Depends(get_db)
):
    """Upload certificate template file"""
    try:
        # Read file content
        file_content = file.file.read()
        
        # Upload file
        file_url = certificate_service.upload_template(file_content, file.filename)
        
        return FileUploadResponse(
            file_url=file_url,
            file_name=file.filename,
            file_size=len(file_content),
            file_type=file.content_type or "application/octet-stream",
            message="Template uploaded successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Certificate Statistics

@router.get("/stats/overview", response_model=CertificateStats)
def get_certificate_stats(
    current_user: User = Depends(require_permission("certificate:read")),
    db: Session = Depends(get_db)
):
    """Get certificate statistics"""
    try:
        stats = certificate_service.get_certificate_stats(db, current_user.id)
        
        return CertificateStats(
            total_certificates=stats["total_certificates"],
            issued_certificates=stats["issued_certificates"],
            valid_certificates=stats["valid_certificates"],
            verified_certificates=stats["verified_certificates"],
            certificates_by_type=stats["certificates_by_type"],
            certificates_by_month=stats["certificates_by_month"],
            top_events=stats["top_events"]
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# User-specific endpoints

@router.get("/my-certificates", response_model=List[CertificateList])
def get_my_certificates(
    skip: int = Query(0, ge=0, description="Skip records"),
    limit: int = Query(100, ge=1, le=1000, description="Limit records"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's certificates"""
    try:
        certificates = certificate_service.get_user_certificates(db, current_user.id, skip, limit)
        
        result = []
        for cert in certificates:
            result.append(CertificateList(
                id=cert.id,
                certificate_id=cert.certificate_id,
                title=cert.title,
                certificate_type=cert.certificate_type,
                participant_name=cert.participant_name,
                event_name=cert.event_name,
                event_date=cert.event_date,
                is_issued=cert.is_issued,
                is_valid=cert.is_valid,
                created_at=cert.created_at
            ))
        
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
