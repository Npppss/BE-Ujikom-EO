from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.dependencies import get_current_active_user, require_permission
from app.db.models import User
from app.services.export_service import export_service
from typing import Optional
import io

router = APIRouter(prefix="/export", tags=["Export Data"])

@router.get("/statistics/excel")
def export_statistics_excel(
    current_user: User = Depends(require_permission("event:read")),
    db: Session = Depends(get_db)
):
    """Export event statistics to Excel format"""
    try:
        # Get user_id for filtering (if not admin, only show their events)
        user_id = None
        if current_user.role.name != "admin":
            user_id = current_user.id
        
        # Generate Excel file
        excel_data = export_service.export_event_statistics(db, user_id, format="excel")
        
        # Create filename with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"statistik_kegiatan_{timestamp}.xlsx"
        
        # Return as streaming response
        return StreamingResponse(
            io.BytesIO(excel_data),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export statistics: {str(e)}")

@router.get("/statistics/csv")
def export_statistics_csv(
    current_user: User = Depends(require_permission("event:read")),
    db: Session = Depends(get_db)
):
    """Export event statistics to CSV format"""
    try:
        # Get user_id for filtering (if not admin, only show their events)
        user_id = None
        if current_user.role.name != "admin":
            user_id = current_user.id
        
        # Generate CSV file
        csv_data = export_service.export_event_statistics(db, user_id, format="csv")
        
        # Create filename with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"statistik_kegiatan_{timestamp}.csv"
        
        # Return as streaming response
        return StreamingResponse(
            io.BytesIO(csv_data),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export statistics: {str(e)}")

@router.get("/participants/excel")
def export_participants_excel(
    event_id: Optional[int] = Query(None, description="Filter by specific event ID"),
    current_user: User = Depends(require_permission("event:read")),
    db: Session = Depends(get_db)
):
    """Export participant data to Excel format"""
    try:
        # Generate Excel file
        excel_data = export_service.export_participant_data(db, event_id, format="excel")
        
        # Create filename with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if event_id:
            filename = f"data_peserta_event_{event_id}_{timestamp}.xlsx"
        else:
            filename = f"data_peserta_semua_{timestamp}.xlsx"
        
        # Return as streaming response
        return StreamingResponse(
            io.BytesIO(excel_data),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export participant data: {str(e)}")

@router.get("/participants/csv")
def export_participants_csv(
    event_id: Optional[int] = Query(None, description="Filter by specific event ID"),
    current_user: User = Depends(require_permission("event:read")),
    db: Session = Depends(get_db)
):
    """Export participant data to CSV format"""
    try:
        # Generate CSV file
        csv_data = export_service.export_participant_data(db, event_id, format="csv")
        
        # Create filename with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if event_id:
            filename = f"data_peserta_event_{event_id}_{timestamp}.csv"
        else:
            filename = f"data_peserta_semua_{timestamp}.csv"
        
        # Return as streaming response
        return StreamingResponse(
            io.BytesIO(csv_data),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export participant data: {str(e)}")

@router.get("/certificates/excel")
def export_certificates_excel(
    event_id: Optional[int] = Query(None, description="Filter by specific event ID"),
    current_user: User = Depends(require_permission("certificate:read")),
    db: Session = Depends(get_db)
):
    """Export certificate data to Excel format"""
    try:
        # Generate Excel file
        excel_data = export_service.export_certificate_data(db, event_id, format="excel")
        
        # Create filename with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if event_id:
            filename = f"data_sertifikat_event_{event_id}_{timestamp}.xlsx"
        else:
            filename = f"data_sertifikat_semua_{timestamp}.xlsx"
        
        # Return as streaming response
        return StreamingResponse(
            io.BytesIO(excel_data),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export certificate data: {str(e)}")

@router.get("/certificates/csv")
def export_certificates_csv(
    event_id: Optional[int] = Query(None, description="Filter by specific event ID"),
    current_user: User = Depends(require_permission("certificate:read")),
    db: Session = Depends(get_db)
):
    """Export certificate data to CSV format"""
    try:
        # Generate CSV file
        csv_data = export_service.export_certificate_data(db, event_id, format="csv")
        
        # Create filename with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if event_id:
            filename = f"data_sertifikat_event_{event_id}_{timestamp}.csv"
        else:
            filename = f"data_sertifikat_semua_{timestamp}.csv"
        
        # Return as streaming response
        return StreamingResponse(
            io.BytesIO(csv_data),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export certificate data: {str(e)}")
