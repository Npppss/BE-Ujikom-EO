# Event Organizer - Attendance System dengan QR Code

Sistem presensi lengkap untuk Event Organizer dengan QR Code untuk check-in dan check-out otomatis.

## Fitur yang Tersedia

### 1. QR Code Management
- **Generate QR Code Check-in**: QR code untuk presensi masuk
- **Generate QR Code Check-out**: QR code untuk presensi keluar
- **QR Code Validation**: Validasi QR code dengan timestamp dan event ID

### 2. Attendance Control
- **Start/Stop Check-in**: Kontrol proses check-in
- **Start/Stop Check-out**: Kontrol proses check-out
- **Real-time Status**: Status check-in/check-out real-time

### 3. Attendance Tracking
- **Automatic Recording**: Pencatatan otomatis saat scan QR
- **Attendance History**: Riwayat presensi per user
- **Event Summary**: Ringkasan presensi per event

### 4. Security Features
- **QR Code Expiry**: QR code expire dalam 24 jam
- **Event-specific QR**: QR code unik per event
- **Permission-based Access**: Akses berdasarkan role dan permission

## Setup dan Instalasi

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Update Database
```bash
python -m app.db.init_db
```

### 3. Jalankan Aplikasi
```bash
uvicorn app.main:app --reload
```

## API Endpoints

### Organizer/Admin Endpoints

#### Start Check-in Process
```http
POST /api/v1/attendance/events/{event_id}/start-check-in
Authorization: Bearer <access_token>
```

#### Stop Check-in Process
```http
POST /api/v1/attendance/events/{event_id}/stop-check-in
Authorization: Bearer <access_token>
```

#### Start Check-out Process
```http
POST /api/v1/attendance/events/{event_id}/start-check-out
Authorization: Bearer <access_token>
```

#### Stop Check-out Process
```http
POST /api/v1/attendance/events/{event_id}/stop-check-out
Authorization: Bearer <access_token>
```

#### Generate Check-in QR Code
```http
GET /api/v1/attendance/events/{event_id}/qr/check-in
Authorization: Bearer <access_token>
```

Response:
```json
{
  "qr_code_data": "{\"type\":\"check_in\",\"event_id\":1,\"qr_code\":\"uuid\",\"timestamp\":\"2024-01-01T10:00:00\"}",
  "qr_code_image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
  "expires_at": null
}
```

#### Generate Check-out QR Code
```http
GET /api/v1/attendance/events/{event_id}/qr/check-out
Authorization: Bearer <access_token>
```

#### Get Event Attendance List
```http
GET /api/v1/attendance/events/{event_id}/list
Authorization: Bearer <access_token>
```

Response:
```json
[
  {
    "id": 1,
    "event_id": 1,
    "user_id": 1,
    "user_name": "John Doe",
    "user_email": "john@example.com",
    "check_in_time": "2024-01-01T10:00:00",
    "check_out_time": "2024-01-01T12:00:00",
    "check_in_qr_scanned": true,
    "check_out_qr_scanned": true,
    "notes": null,
    "created_at": "2024-01-01T09:00:00"
  }
]
```

#### Get Attendance Summary
```http
GET /api/v1/attendance/events/{event_id}/summary
Authorization: Bearer <access_token>
```

Response:
```json
{
  "event_id": 1,
  "event_title": "Sample Event",
  "total_registered": 10,
  "total_checked_in": 8,
  "total_checked_out": 6,
  "check_in_started": true,
  "check_out_started": true
}
```

### User Endpoints

#### Scan Check-in QR Code
```http
POST /api/v1/attendance/scan/check-in
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "qr_code": "{\"type\":\"check_in\",\"event_id\":1,\"qr_code\":\"uuid\",\"timestamp\":\"2024-01-01T10:00:00\"}",
  "event_id": 1
}
```

Response:
```json
{
  "message": "Check-in successful",
  "check_in_time": "2024-01-01T10:00:00",
  "user_name": "John Doe",
  "event_title": "Sample Event"
}
```

#### Scan Check-out QR Code
```http
POST /api/v1/attendance/scan/check-out
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "qr_code": "{\"type\":\"check_out\",\"event_id\":1,\"qr_code\":\"uuid\",\"timestamp\":\"2024-01-01T12:00:00\"}",
  "event_id": 1
}
```

#### Universal QR Scanner (Mobile Apps)
```http
POST /api/v1/attendance/scan/qr
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "qr_code": "{\"type\":\"check_in\",\"event_id\":1,\"qr_code\":\"uuid\",\"timestamp\":\"2024-01-01T10:00:00\"}",
  "event_id": 1
}
```

Response:
```json
{
  "type": "check_in",
  "message": "Check-in successful",
  "check_in_time": "2024-01-01T10:00:00",
  "user_name": "John Doe",
  "event_title": "Sample Event"
}
```

#### Get My Attendance History
```http
GET /api/v1/attendance/my-attendance
Authorization: Bearer <access_token>
```

## Workflow Sistem Presensi

### 1. Persiapan Event (Organizer/Admin)
1. **Start Check-in**: Aktifkan proses check-in
2. **Generate QR Code**: Ambil QR code check-in
3. **Display QR Code**: Tampilkan QR code di lokasi event

### 2. Check-in Process (User)
1. **Scan QR Code**: User scan QR code check-in
2. **Automatic Recording**: Sistem mencatat presensi otomatis
3. **Confirmation**: User mendapat konfirmasi check-in

### 3. Check-out Process (User)
1. **Start Check-out**: Organizer aktifkan check-out
2. **Generate QR Code**: Ambil QR code check-out
3. **Scan QR Code**: User scan QR code check-out
4. **Automatic Recording**: Sistem mencatat check-out

### 4. Monitoring (Organizer/Admin)
1. **Real-time Status**: Lihat status check-in/check-out
2. **Attendance List**: Lihat daftar presensi
3. **Summary Report**: Lihat ringkasan presensi

## QR Code Format

### Check-in QR Code Data
```json
{
  "type": "check_in",
  "event_id": 1,
  "qr_code": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T10:00:00"
}
```

### Check-out QR Code Data
```json
{
  "type": "check_out",
  "event_id": 1,
  "qr_code": "550e8400-e29b-41d4-a716-446655440001",
  "timestamp": "2024-01-01T12:00:00"
}
```

## Database Schema

### Event Table (Updated)
```sql
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    description VARCHAR,
    date DATE NOT NULL,
    time TIME NOT NULL,
    location VARCHAR NOT NULL,
    flyer_url VARCHAR,
    is_active BOOLEAN DEFAULT TRUE,
    check_in_started BOOLEAN DEFAULT FALSE,
    check_out_started BOOLEAN DEFAULT FALSE,
    check_in_qr_code VARCHAR UNIQUE,
    check_out_qr_code VARCHAR UNIQUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);
```

### Attendance Table
```sql
CREATE TABLE attendances (
    id SERIAL PRIMARY KEY,
    event_id INTEGER REFERENCES events(id),
    user_id INTEGER REFERENCES users(id),
    check_in_time TIMESTAMP,
    check_out_time TIMESTAMP,
    check_in_qr_scanned BOOLEAN DEFAULT FALSE,
    check_out_qr_scanned BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);
```

## Security Features

### 1. QR Code Security
- **Unique QR Codes**: Setiap event memiliki QR code unik
- **Timestamp Validation**: QR code expire dalam 24 jam
- **Event-specific**: QR code hanya valid untuk event tertentu

### 2. Permission Control
- **Organizer/Admin**: Dapat mengelola attendance
- **User**: Hanya dapat scan QR code
- **Role-based Access**: Berdasarkan permission

### 3. Data Integrity
- **Automatic Recording**: Pencatatan otomatis saat scan
- **Duplicate Prevention**: Mencegah check-in/check-out ganda
- **Audit Trail**: Riwayat lengkap presensi

## Testing

### Test QR Code Generation
```bash
# Login sebagai admin/organizer
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@eventorganizer.com","password":"admin123"}'

# Generate check-in QR code
curl -X GET "http://localhost:8000/api/v1/attendance/events/1/qr/check-in" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Test QR Code Scanning
```bash
# Login sebagai user
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'

# Scan QR code
curl -X POST "http://localhost:8000/api/v1/attendance/scan/qr" \
  -H "Authorization: Bearer USER_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"qr_code":"QR_CODE_DATA_FROM_GENERATION","event_id":1}'
```

## Mobile App Integration

### QR Code Scanning
```javascript
// Example React Native code
import QRCodeScanner from 'react-native-qrcode-scanner';

const scanQRCode = (qrData) => {
  fetch('http://localhost:8000/api/v1/attendance/scan/qr', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      qr_code: qrData,
      event_id: eventId
    })
  })
  .then(response => response.json())
  .then(data => {
    console.log('Attendance recorded:', data);
  });
};
```

### QR Code Display
```javascript
// Example React code untuk menampilkan QR code
import QRCode from 'qrcode.react';

const QRCodeDisplay = ({ qrData }) => {
  return (
    <div>
      <QRCode value={qrData} size={256} />
      <p>Scan this QR code to check in/out</p>
    </div>
  );
};
```

## Production Considerations

### 1. Performance
- **QR Code Caching**: Cache QR code images
- **Database Indexing**: Index pada event_id dan user_id
- **Connection Pooling**: Optimize database connections

### 2. Security
- **HTTPS**: Gunakan HTTPS di production
- **Rate Limiting**: Batasi request per user
- **QR Code Rotation**: Rotate QR codes secara berkala

### 3. Monitoring
- **Attendance Analytics**: Track attendance patterns
- **Error Logging**: Log semua error dan exceptions
- **Performance Metrics**: Monitor response times

### 4. Scalability
- **Load Balancing**: Untuk traffic tinggi
- **Database Sharding**: Untuk data besar
- **CDN**: Untuk QR code images

## Troubleshooting

### Common Issues

1. **QR Code Not Working**
   - Periksa apakah check-in/check-out sudah dimulai
   - Pastikan QR code tidak expired
   - Verifikasi event_id di QR code

2. **Duplicate Check-in**
   - Sistem mencegah check-in ganda
   - Periksa status check_in_qr_scanned

3. **Permission Denied**
   - Periksa role dan permissions user
   - Pastikan user sudah login

4. **QR Code Expired**
   - Generate QR code baru
   - QR code expire dalam 24 jam 