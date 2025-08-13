# Event Organizer - Time Validation System

Sistem validasi waktu lengkap untuk Event Organizer yang memastikan event dan attendance sesuai dengan aturan waktu yang ditentukan.

## 🕐 Fitur Validasi Waktu

### 1. **Validasi Waktu Pendaftaran Event (H-3)**
- **Admin/Organizer** hanya dapat membuat event maksimal **H-3** dari tanggal penyelenggaraan
- **Auto-publish** event jika validasi H-3 berhasil
- **Validasi update** event untuk memastikan tetap memenuhi syarat H-3
- **Validasi publish** event untuk memastikan tidak melanggar aturan

### 2. **Validasi Waktu Pendaftaran Event (H-0)**
- **Peserta** hanya dapat mendaftar maksimal hingga **H-0** (hari H) sebelum event dimulai
- **Formulir tertutup otomatis** saat event dimulai
- **Real-time validation** untuk deadline pendaftaran

### 3. **Validasi Waktu Daftar Hadir**
- **Check-in** hanya dapat dilakukan pada **hari H setelah jam event dimulai**
- **Check-out** hanya dapat dilakukan setelah event dimulai
- **Tombol daftar hadir** tidak aktif sebelum waktu yang ditentukan

## 🔧 Implementasi

### **Event Service Validations**

#### 1. Create Event (H-3 Validation)
```python
def create_event(self, db: Session, event_data: EventCreate, organizer_id: int) -> Event:
    # Validasi H-3: Event hanya dapat dibuat maksimal H-3 dari tanggal penyelenggaraan
    event_start_date = event_data.start_date
    current_date = datetime.now().date()
    min_creation_date = event_start_date - timedelta(days=3)
    
    if current_date > min_creation_date:
        raise Exception(f"Event hanya dapat dibuat maksimal H-3 dari tanggal penyelenggaraan. "
                      f"Tanggal event: {event_start_date}, "
                      f"Batas pembuatan: {min_creation_date}, "
                      f"Tanggal hari ini: {current_date}")
    
    # Auto-publish jika validasi berhasil
    event = Event(
        **event_dict,
        organizer_id=organizer_id,
        status=EventStatus.PUBLISHED
    )
```

#### 2. Update Event (H-3 Validation)
```python
def update_event(self, db: Session, event_id: int, event_data: EventUpdate, user_id: int) -> Optional[Event]:
    # Validasi H-3: Jika mengubah tanggal event, harus tetap memenuhi syarat H-3
    if event_data.start_date:
        new_start_date = event_data.start_date
        current_date = datetime.now().date()
        min_creation_date = new_start_date - timedelta(days=3)
        
        if current_date > min_creation_date:
            raise Exception(f"Tanggal event tidak dapat diubah ke {new_start_date} karena melanggar aturan H-3. "
                          f"Batas pembuatan: {min_creation_date}, "
                          f"Tanggal hari ini: {current_date}")
```

#### 3. Publish Event (H-3 Validation)
```python
def publish_event(self, db: Session, event_id: int, user_id: int) -> Optional[Event]:
    # Validasi H-3: Event hanya dapat dipublish jika memenuhi syarat H-3
    current_date = datetime.now().date()
    min_creation_date = event.start_date - timedelta(days=3)
    
    if current_date > min_creation_date:
        raise Exception(f"Event tidak dapat dipublish karena melanggar aturan H-3. "
                      f"Tanggal event: {event.start_date}, "
                      f"Batas pembuatan: {min_creation_date}, "
                      f"Tanggal hari ini: {current_date}")
```

#### 4. Event Registration (H-0 Validation)
```python
def register_for_event(self, db: Session, event_id: int, user_id: int, registration_data: dict) -> Optional[EventRegistration]:
    # Validasi waktu pendaftaran: Pendaftaran maksimal H-0 (hari H) dan sebelum jam event dimulai
    current_datetime = datetime.now()
    event_datetime = datetime.combine(event.start_date, event.start_time)
    
    if current_datetime >= event_datetime:
        raise Exception(f"Pendaftaran sudah ditutup. Event dimulai pada {event_datetime.strftime('%d/%m/%Y %H:%M')}")
```

### **Attendance Service Validations**

#### 1. Check-in Validation
```python
def scan_check_in_qr(self, db: Session, qr_data: str, user_id: int) -> dict:
    # Validasi waktu daftar hadir: Check-in hanya dapat dilakukan pada hari H setelah jam event dimulai
    current_datetime = datetime.now()
    event_datetime = datetime.combine(event.start_date, event.start_time)
    
    if current_datetime < event_datetime:
        raise Exception(f"Check-in belum dapat dilakukan. Event dimulai pada {event_datetime.strftime('%d/%m/%Y %H:%M')}")
```

#### 2. Check-out Validation
```python
def scan_check_out_qr(self, db: Session, qr_data: str, user_id: int) -> dict:
    # Validasi waktu daftar hadir: Check-out hanya dapat dilakukan setelah event dimulai
    current_datetime = datetime.now()
    event_datetime = datetime.combine(event.start_date, event.start_time)
    
    if current_datetime < event_datetime:
        raise Exception(f"Check-out belum dapat dilakukan. Event dimulai pada {event_datetime.strftime('%d/%m/%Y %H:%M')}")
```

#### 3. Helper Methods
```python
def can_attend_event(self, event: Event) -> tuple[bool, str]:
    """
    Validasi apakah user dapat melakukan daftar hadir
    Returns: (can_attend, message)
    """
    current_datetime = datetime.now()
    event_datetime = datetime.combine(event.start_date, event.start_time)
    
    if current_datetime < event_datetime:
        return False, f"Check-in/Check-out belum dapat dilakukan. Event dimulai pada {event_datetime.strftime('%d/%m/%Y %H:%M')}"
    
    return True, "Event dapat dihadiri"

def is_event_ongoing(self, event: Event) -> bool:
    """Check apakah event sedang berlangsung"""
    current_datetime = datetime.now()
    event_start = datetime.combine(event.start_date, event.start_time)
    event_end = datetime.combine(event.end_date, event.end_time)
    
    return event_start <= current_datetime <= event_end
```

## 📋 Test Cases

### **Event Creation H-3 Validation**
| Test Case | Start Date | Expected Result |
|-----------|------------|-----------------|
| Event H-5 | Today + 5 days | ✅ SUCCESS |
| Event H-3 | Today + 3 days | ✅ SUCCESS (Batas) |
| Event H-2 | Today + 2 days | ❌ ERROR |
| Event H-1 | Today + 1 day | ❌ ERROR |
| Event H+0 | Today | ❌ ERROR |

### **Event Registration Deadline**
| Test Case | Start Date | Start Time | Expected Result |
|-----------|------------|------------|-----------------|
| Event H+1 | Today + 1 day | Today + 1 hour | ✅ CAN_REGISTER |
| Event H+0 | Today | Today + 1 hour | ✅ CAN_REGISTER |
| Event H+0 | Today | Today | ❌ CANNOT_REGISTER |
| Event H-1 | Today - 1 day | Today | ❌ CANNOT_REGISTER |

### **Attendance Time Validation**
| Test Case | Start Date | Start Time | Expected Result |
|-----------|------------|------------|-----------------|
| Event H+1 | Today + 1 day | Today + 1 hour | ❌ CANNOT_ATTEND |
| Event H+0 | Today | Today + 1 hour | ❌ CANNOT_ATTEND |
| Event H+0 | Today | Today | ✅ CAN_ATTEND |
| Event H-1 | Today - 1 day | Today | ✅ CAN_ATTEND |

## 🚀 API Endpoints

### **Create Event (with H-3 validation)**
```http
POST /api/v1/events/
Authorization: Bearer <organizer_token>
Content-Type: application/json

{
  "title": "Test Event",
  "start_date": "2024-12-25",
  "end_date": "2024-12-25",
  "start_time": "10:00:00",
  "end_time": "12:00:00",
  "location": "Test Location",
  "description": "Test Description"
}
```

**Success Response (H-3 valid):**
```json
{
  "id": 1,
  "title": "Test Event",
  "status": "published",
  "start_date": "2024-12-25",
  "created_at": "2024-12-22T10:00:00"
}
```

**Error Response (H-3 invalid):**
```json
{
  "detail": "Event hanya dapat dibuat maksimal H-3 dari tanggal penyelenggaraan. Tanggal event: 2024-12-25, Batas pembuatan: 2024-12-22, Tanggal hari ini: 2024-12-23"
}
```

### **Register for Event (with deadline validation)**
```http
POST /api/v1/events/{event_id}/register
Authorization: Bearer <user_token>
Content-Type: application/json

{
  "ticket_type": "regular",
  "special_requirements": "None"
}
```

**Success Response (before deadline):**
```json
{
  "message": "Registration successful",
  "status": "confirmed"
}
```

**Error Response (after deadline):**
```json
{
  "detail": "Pendaftaran sudah ditutup. Event dimulai pada 25/12/2024 10:00"
}
```

### **Check-in Attendance (with time validation)**
```http
POST /api/v1/attendance/scan-check-in
Authorization: Bearer <user_token>
Content-Type: application/json

{
  "qr_code": "qr_data_here",
  "event_id": 1
}
```

**Success Response (after event starts):**
```json
{
  "message": "Check-in successful",
  "check_in_time": "2024-12-25T10:15:00",
  "user_name": "John Doe",
  "event_title": "Test Event"
}
```

**Error Response (before event starts):**
```json
{
  "detail": "Check-in belum dapat dilakukan. Event dimulai pada 25/12/2024 10:00"
}
```

## 🔍 Testing

### **Run Time Validation Tests**
```bash
# Test validasi waktu
python examples/time_validation_test.py
```

### **Test Specific Validations**
```python
# Test H-3 validation
from app.services.event_service import EventService
event_service = EventService()

# Test attendance time validation
from app.services.attendance_service import AttendanceService
attendance_service = AttendanceService()

# Test helper methods
can_attend, message = attendance_service.can_attend_event(event)
is_ongoing = attendance_service.is_event_ongoing(event)
```

## 📱 Frontend Integration

### **Real-time Deadline Countdown**
```javascript
// Countdown timer untuk deadline pendaftaran
const countdownToEvent = (eventStartDate, eventStartTime) => {
  const eventDateTime = new Date(`${eventStartDate}T${eventStartTime}`);
  const now = new Date();
  
  if (now >= eventDateTime) {
    return { canRegister: false, message: "Pendaftaran sudah ditutup" };
  }
  
  const timeLeft = eventDateTime - now;
  const days = Math.floor(timeLeft / (1000 * 60 * 60 * 24));
  const hours = Math.floor((timeLeft % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  
  return { 
    canRegister: true, 
    timeLeft: `${days}d ${hours}h`,
    message: "Masih bisa mendaftar"
  };
};
```

### **Dynamic Attendance Button**
```javascript
// Tombol daftar hadir yang dinamis
const AttendanceButton = ({ event, user }) => {
  const canAttend = new Date() >= new Date(`${event.start_date}T${event.start_time}`);
  
  if (!canAttend) {
    return (
      <button disabled className="btn-disabled">
        Check-in belum tersedia
      </button>
    );
  }
  
  return (
    <button className="btn-primary" onClick={handleCheckIn}>
      Check-in Sekarang
    </button>
  );
};
```

## 🎯 Business Rules

### **1. Event Creation Rules**
- **H-3 Rule**: Event harus dibuat minimal 3 hari sebelum penyelenggaraan
- **Auto-publish**: Event otomatis published jika memenuhi H-3
- **Update Protection**: Tanggal event tidak bisa diubah melanggar H-3

### **2. Registration Rules**
- **Deadline**: Pendaftaran ditutup saat event dimulai
- **Real-time**: Validasi real-time untuk deadline
- **User Experience**: Pesan error yang jelas dan informatif

### **3. Attendance Rules**
- **Check-in Time**: Hanya setelah event dimulai
- **Check-out Time**: Hanya setelah event dimulai
- **QR Code Security**: QR code hanya aktif pada waktu yang tepat

## 🚨 Error Handling

### **Common Error Messages**
1. **H-3 Validation Error**: "Event hanya dapat dibuat maksimal H-3 dari tanggal penyelenggaraan"
2. **Registration Deadline Error**: "Pendaftaran sudah ditutup. Event dimulai pada [datetime]"
3. **Attendance Time Error**: "Check-in belum dapat dilakukan. Event dimulai pada [datetime]"

### **Error Response Format**
```json
{
  "detail": "Error message dengan detail waktu yang jelas",
  "error_type": "validation_error",
  "field": "start_date|registration_time|attendance_time"
}
```

## 🔮 Future Enhancements

### **1. Advanced Time Rules**
- **Custom Deadlines**: Deadline yang dapat dikustomisasi per event
- **Time Zones**: Support untuk multiple time zones
- **Recurring Events**: Validasi untuk event yang berulang

### **2. Smart Notifications**
- **Deadline Reminders**: Notifikasi otomatis untuk deadline
- **Time Alerts**: Alert saat waktu check-in/check-out tersedia
- **Schedule Conflicts**: Deteksi konflik jadwal

### **3. Analytics & Reporting**
- **Time Compliance**: Report kepatuhan aturan waktu
- **Registration Patterns**: Analisis pola pendaftaran
- **Attendance Timing**: Analisis waktu kehadiran

---

**Time Validation System Ready for Production Use** 🎯
