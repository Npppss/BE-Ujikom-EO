import qrcode
import base64
import io
from datetime import datetime, timedelta
from typing import Optional
import json

class QRCodeService:
    def __init__(self):
        pass
    
    def generate_qr_code(self, data: str, size: int = 10) -> str:
        """Generate QR code and return as base64 encoded image"""
        # Create QR code instance
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=size,
            border=4,
        )
        
        # Add data to QR code
        qr.add_data(data)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return img_str
    
    def generate_check_in_qr_data(self, event_id: int, qr_code: str) -> str:
        """Generate QR code data for check-in"""
        data = {
            "type": "check_in",
            "event_id": event_id,
            "qr_code": qr_code,
            "timestamp": datetime.utcnow().isoformat()
        }
        return json.dumps(data)
    
    def generate_check_out_qr_data(self, event_id: int, qr_code: str) -> str:
        """Generate QR code data for check-out"""
        data = {
            "type": "check_out",
            "event_id": event_id,
            "qr_code": qr_code,
            "timestamp": datetime.utcnow().isoformat()
        }
        return json.dumps(data)
    
    def parse_qr_data(self, qr_data: str) -> Optional[dict]:
        """Parse QR code data"""
        try:
            return json.loads(qr_data)
        except (json.JSONDecodeError, KeyError):
            return None
    
    def validate_qr_code(self, qr_data: dict, event_id: int, qr_type: str) -> bool:
        """Validate QR code data"""
        if not qr_data:
            return False
        
        # Check if QR code type matches
        if qr_data.get("type") != qr_type:
            return False
        
        # Check if event ID matches
        if qr_data.get("event_id") != event_id:
            return False
        
        # Check if QR code is not too old (optional, for security)
        timestamp_str = qr_data.get("timestamp")
        if timestamp_str:
            try:
                timestamp = datetime.fromisoformat(timestamp_str)
                # QR code should not be older than 24 hours
                if datetime.utcnow() - timestamp > timedelta(hours=24):
                    return False
            except ValueError:
                return False
        
        return True

# Create service instance
qr_service = QRCodeService() 