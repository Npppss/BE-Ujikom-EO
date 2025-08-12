import pandas as pd
import io
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.db.models import Event, EventRegistration, Attendance, User, EventStatus, EventCategory, Certificate
from typing import Dict, Any, List, Optional
import os

class ExportService:
    def __init__(self):
        pass
    
    def export_event_statistics(self, db: Session, user_id: Optional[int] = None, format: str = "excel") -> bytes:
        """Export event statistics to Excel or CSV"""
        # Get event statistics
        query = db.query(Event)
        if user_id:
            query = query.filter(Event.organizer_id == user_id)
        
        events = query.all()
        
        # Prepare monthly statistics data
        monthly_data = []
        for i in range(12):
            month_date = datetime.utcnow() - timedelta(days=30*i)
            month_events = [e for e in events if e.created_at.month == month_date.month and e.created_at.year == month_date.year]
            
            # Count completed events (terlaksana)
            completed_events = [e for e in month_events if e.status == EventStatus.COMPLETED]
            
            # Count participants who attended (mengisi daftar hadir)
            total_attendances = 0
            for event in completed_events:
                attendances = db.query(Attendance).filter(
                    Attendance.event_id == event.id,
                    Attendance.check_in_qr_scanned == True
                ).count()
                total_attendances += attendances
            
            monthly_data.append({
                "Bulan": month_date.strftime("%B %Y"),
                "Jumlah Kegiatan Terlaksana": len(completed_events),
                "Jumlah Peserta Hadir": total_attendances
            })
        
        # Prepare top 10 events by participant count
        top_events_data = []
        event_participant_counts = []
        
        for event in events:
            if event.status == EventStatus.COMPLETED:
                attendances = db.query(Attendance).filter(
                    Attendance.event_id == event.id,
                    Attendance.check_in_qr_scanned == True
                ).count()
                event_participant_counts.append({
                    "event": event,
                    "participant_count": attendances
                })
        
        # Sort by participant count and get top 10
        event_participant_counts.sort(key=lambda x: x["participant_count"], reverse=True)
        top_10_events = event_participant_counts[:10]
        
        for i, item in enumerate(top_10_events, 1):
            event = item["event"]
            top_events_data.append({
                "Peringkat": i,
                "Judul Kegiatan": event.title,
                "Kategori": event.category.value,
                "Tanggal": event.start_date.strftime("%d/%m/%Y"),
                "Jumlah Peserta": item["participant_count"],
                "Lokasi": event.location
            })
        
        # Create DataFrames
        monthly_df = pd.DataFrame(monthly_data)
        top_events_df = pd.DataFrame(top_events_data)
        
        if format.lower() == "csv":
            # Export to CSV
            output = io.StringIO()
            
            # Write monthly statistics
            output.write("STATISTIK KEGIATAN PER BULAN\n")
            output.write("=" * 50 + "\n")
            monthly_df.to_csv(output, index=False, sep=',')
            output.write("\n\n")
            
            # Write top events
            output.write("10 KEGIATAN DENGAN PESERTA TERBANYAK\n")
            output.write("=" * 50 + "\n")
            top_events_df.to_csv(output, index=False, sep=',')
            
            return output.getvalue().encode('utf-8')
        
        else:  # Excel format
            # Create Excel file in memory
            output = io.BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # Write monthly statistics
                monthly_df.to_excel(writer, sheet_name='Statistik Bulanan', index=False)
                
                # Write top events
                top_events_df.to_excel(writer, sheet_name='Top 10 Kegiatan', index=False)
                
                # Auto-adjust column widths
                for sheet_name in writer.sheets:
                    worksheet = writer.sheets[sheet_name]
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column_letter].width = adjusted_width
            
            output.seek(0)
            return output.getvalue()
    
    def export_participant_data(self, db: Session, event_id: Optional[int] = None, format: str = "excel") -> bytes:
        """Export participant data to Excel or CSV"""
        # Build query for participant data
        query = db.query(
            User.full_name,
            User.email,
            Event.title.label('event_title'),
            Event.start_date,
            Event.location,
            EventRegistration.registration_date,
            EventRegistration.status.label('registration_status'),
            EventRegistration.ticket_type,
            EventRegistration.price_paid,
            Attendance.check_in_time,
            Attendance.check_out_time,
            Attendance.check_in_qr_scanned,
            Attendance.check_out_qr_scanned
        ).join(
            EventRegistration, User.id == EventRegistration.user_id
        ).join(
            Event, EventRegistration.event_id == Event.id
        ).outerjoin(
            Attendance, (User.id == Attendance.user_id) & (Event.id == Attendance.event_id)
        )
        
        if event_id:
            query = query.filter(Event.id == event_id)
        
        # Execute query
        results = query.all()
        
        # Convert to list of dictionaries
        participant_data = []
        for result in results:
            participant_data.append({
                "Nama Lengkap": result.full_name or "N/A",
                "Email": result.email,
                "Judul Kegiatan": result.event_title,
                "Tanggal Kegiatan": result.start_date.strftime("%d/%m/%Y") if result.start_date else "N/A",
                "Lokasi": result.location,
                "Tanggal Registrasi": result.registration_date.strftime("%d/%m/%Y %H:%M") if result.registration_date else "N/A",
                "Status Registrasi": result.registration_status,
                "Tipe Tiket": result.ticket_type or "N/A",
                "Harga Dibayar": f"Rp {result.price_paid:,.0f}" if result.price_paid else "Gratis",
                "Waktu Check-in": result.check_in_time.strftime("%d/%m/%Y %H:%M") if result.check_in_time else "Belum Check-in",
                "Waktu Check-out": result.check_out_time.strftime("%d/%m/%Y %H:%M") if result.check_out_time else "Belum Check-out",
                "Status Check-in": "Hadir" if result.check_in_qr_scanned else "Tidak Hadir",
                "Status Check-out": "Check-out" if result.check_out_qr_scanned else "Belum Check-out"
            })
        
        # Create DataFrame
        df = pd.DataFrame(participant_data)
        
        if format.lower() == "csv":
            # Export to CSV
            output = io.StringIO()
            df.to_csv(output, index=False, sep=',', encoding='utf-8')
            return output.getvalue().encode('utf-8')
        
        else:  # Excel format
            # Create Excel file in memory
            output = io.BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Data Peserta', index=False)
                
                # Auto-adjust column widths
                worksheet = writer.sheets['Data Peserta']
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            output.seek(0)
            return output.getvalue()
    
    def export_certificate_data(self, db: Session, event_id: Optional[int] = None, format: str = "excel") -> bytes:
        """Export certificate data to Excel or CSV"""
        
        # Build query for certificate data
        query = db.query(
            Certificate.certificate_id,
            Certificate.participant_name,
            Certificate.event_name,
            Certificate.event_date,
            Certificate.certificate_type,
            Certificate.is_issued,
            Certificate.issued_date,
            Certificate.is_valid,
            Certificate.is_verified,
            Certificate.verified_at,
            User.email
        ).join(
            User, Certificate.user_id == User.id
        )
        
        if event_id:
            query = query.filter(Certificate.event_id == event_id)
        
        # Execute query
        results = query.all()
        
        # Convert to list of dictionaries
        certificate_data = []
        for result in results:
            certificate_data.append({
                "ID Sertifikat": result.certificate_id,
                "Nama Peserta": result.participant_name,
                "Email": result.email,
                "Nama Kegiatan": result.event_name,
                "Tanggal Kegiatan": result.event_date.strftime("%d/%m/%Y") if result.event_date else "N/A",
                "Tipe Sertifikat": result.certificate_type,
                "Status Terbit": "Terbit" if result.is_issued else "Belum Terbit",
                "Tanggal Terbit": result.issued_date.strftime("%d/%m/%Y") if result.issued_date else "N/A",
                "Status Valid": "Valid" if result.is_valid else "Tidak Valid",
                "Status Verifikasi": "Terverifikasi" if result.is_verified else "Belum Verifikasi",
                "Tanggal Verifikasi": result.verified_at.strftime("%d/%m/%Y %H:%M") if result.verified_at else "N/A"
            })
        
        # Create DataFrame
        df = pd.DataFrame(certificate_data)
        
        if format.lower() == "csv":
            # Export to CSV
            output = io.StringIO()
            df.to_csv(output, index=False, sep=',', encoding='utf-8')
            return output.getvalue().encode('utf-8')
        
        else:  # Excel format
            # Create Excel file in memory
            output = io.BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Data Sertifikat', index=False)
                
                # Auto-adjust column widths
                worksheet = writer.sheets['Data Sertifikat']
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            output.seek(0)
            return output.getvalue()

# Create instance
export_service = ExportService()
