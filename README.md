# Event Organizer Backend

Backend API untuk sistem manajemen event dan sertifikat dengan fitur lengkap autentikasi, manajemen user, tracking kehadiran, dan export data.

## Fitur Utama

### 🔐 Authentication & Authorization
- **JWT-based authentication** dengan access dan refresh token
- **Role-based access control (RBAC)** dengan roles: admin, organizer, user
- **Email verification** dengan token OTP
- **Password reset** dengan email verification
- **Password strength validation** menggunakan regex
- **Session timeout** dengan durasi berbeda berdasarkan role:
  - Admin dan User Management: 5 menit
  - User biasa: 10 menit

### 📊 Event Management
- **CRUD operations** untuk event dengan validasi waktu
- **Event registration** dengan validasi H-0 (maksimal sampai event dimulai)
- **Event creation** dengan validasi H-3 (maksimal 3 hari sebelum event)
- **Event categories** dan status management
- **Event search** dan filtering

### 👥 User Management
- **User registration** dengan verifikasi email
- **User roles** dan permissions management
- **User profile** management
- **Session management** dengan auto logout

### 📈 Attendance Tracking
- **QR code generation** untuk check-in/check-out
- **Attendance validation** dengan waktu event
- **Attendance history** dan reporting
- **Real-time attendance** status

### 🏆 Certificate Management
- **Certificate generation** otomatis
- **Certificate templates** customization
- **Certificate verification** system
- **Certificate export** functionality

### 📤 Data Export
- **Excel export** (.xlsx) untuk semua data
- **CSV export** untuk data analysis
- **Event statistics** export
- **Participant data** export
- **Certificate data** export

## Teknologi yang Digunakan

- **FastAPI** - Modern, fast web framework
- **PostgreSQL** - Relational database
- **SQLAlchemy** - ORM untuk database
- **Pydantic** - Data validation dan serialization
- **JWT** - JSON Web Tokens untuk authentication
- **Pandas** - Data manipulation dan export
- **OpenPyXL** - Excel file generation
- **Bcrypt** - Password hashing
- **Python-dotenv** - Environment configuration

## Struktur File

```
event_organizer_backend/
├── app/
│   ├── api/v1/endpoints/     # API endpoints
│   ├── core/                 # Core configuration
│   ├── db/                   # Database models dan connection
│   ├── middleware/           # Custom middleware
│   ├── services/             # Business logic
│   ├── utils/                # Utility functions
│   └── main.py              # FastAPI application
├── examples/                 # Test scripts dan examples
├── requirements.txt          # Python dependencies
├── README.md                 # Main documentation
├── README_EXPORT.md          # Export feature documentation
├── README_PASSWORD_VALIDATION.md  # Password validation docs
├── README_TIME_VALIDATION.md      # Time validation docs
├── README_SESSION_TIMEOUT.md      # Session timeout docs
└── .gitignore               # Git ignore patterns
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - User logout
- `POST /api/v1/auth/forgot-password` - Forgot password
- `POST /api/v1/auth/reset-password` - Reset password
- `POST /api/v1/auth/change-password` - Change password
- `POST /api/v1/auth/verify-email` - Email verification
- `GET /api/v1/auth/session-status` - Check session status
- `GET /api/v1/auth/password-requirements` - Get password requirements
- `POST /api/v1/auth/validate-password` - Validate password strength

### User Management
- `GET /api/v1/users/` - Get all users (admin only)
- `GET /api/v1/users/{user_id}` - Get user by ID
- `PUT /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Delete user (admin only)

### Event Management
- `GET /api/v1/events/` - Get all events
- `POST /api/v1/events/` - Create new event
- `GET /api/v1/events/{event_id}` - Get event by ID
- `PUT /api/v1/events/{event_id}` - Update event
- `DELETE /api/v1/events/{event_id}` - Delete event
- `POST /api/v1/events/{event_id}/publish` - Publish event
- `POST /api/v1/events/{event_id}/register` - Register for event

### Attendance
- `POST /api/v1/attendance/check-in` - Check-in attendance
- `POST /api/v1/attendance/check-out` - Check-out attendance
- `GET /api/v1/attendance/event/{event_id}` - Get event attendance

### Certificates
- `GET /api/v1/certificates/` - Get all certificates
- `GET /api/v1/certificates/{certificate_id}` - Get certificate by ID
- `POST /api/v1/certificates/generate` - Generate certificate

### Data Export
- `GET /api/v1/export/statistics/excel` - Export statistics to Excel
- `GET /api/v1/export/statistics/csv` - Export statistics to CSV
- `GET /api/v1/export/participants/excel` - Export participants to Excel
- `GET /api/v1/export/participants/csv` - Export participants to CSV
- `GET /api/v1/export/certificates/excel` - Export certificates to Excel
- `GET /api/v1/export/certificates/csv` - Export certificates to CSV

## Setup dan Instalasi

### 1. Clone Repository
```bash
git clone https://github.com/Npppss/BE-Ujikom-EO
cd event_organizer_backend
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Buat file `.env` dengan konfigurasi berikut:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/event_organizer

# Security Configuration
SECRET_KEY=your-secret-key-here-make-it-long-and-random
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Session timeout configuration
ADMIN_SESSION_TIMEOUT_MINUTES=5      # 5 menit untuk admin dan user management
USER_SESSION_TIMEOUT_MINUTES=10      # 10 menit untuk user biasa

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com

# Frontend URL
FRONTEND_URL=http://localhost:3000
```

### 4. Database Setup
```bash
# Buat database PostgreSQL
createdb event_organizer

# Jalankan migrasi (jika ada)
python -m app.db.init_db
```

### 5. Run Application
```bash
uvicorn app.main:app --reload
```

Aplikasi akan berjalan di `http://localhost:8000`

## Fitur Session Timeout

Sistem menerapkan session timeout yang berbeda berdasarkan role user:

### ⏰ Timeout Durations
- **Admin & Organizer**: 5 menit (untuk keamanan tinggi)
- **User Biasa**: 10 menit (untuk user experience)

### 🔒 Security Features
- **Automatic validation** setiap request
- **Auto logout** ketika session expired
- **Response headers** dengan informasi session
- **Session status endpoint** untuk monitoring

### 📱 Frontend Integration
- **JavaScript timers** untuk countdown
- **Auto redirect** ke login page
- **Session warning** sebelum expired
- **Real-time status** checking

## Testing

### Run Test Scripts
```bash
# Test session timeout
python examples/session_timeout_test.py

# Test export functionality
python examples/export_example.py

# Test password validation
python examples/password_validation_test.py

# Test time validation
python examples/time_validation_simple_test.py
```

### API Documentation
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Dokumentasi Tambahan

- **[README_EXPORT.md](README_EXPORT.md)** - Dokumentasi fitur export data
- **[README_PASSWORD_VALIDATION.md](README_PASSWORD_VALIDATION.md)** - Dokumentasi validasi password
- **[README_TIME_VALIDATION.md](README_TIME_VALIDATION.md)** - Dokumentasi validasi waktu
- **[README_SESSION_TIMEOUT.md](README_SESSION_TIMEOUT.md)** - Dokumentasi session timeout

## Roadmap

### ✅ Completed Features
- [x] Authentication system dengan JWT
- [x] Role-based access control
- [x] User management
- [x] Event management
- [x] Attendance tracking
- [x] Certificate management
- [x] Data export (Excel/CSV)
- [x] Password strength validation
- [x] Time-based validations (H-3, H-0)
- [x] Session timeout system

### 🚧 In Progress
- [ ] Mobile responsive interface
- [ ] Progressive Web App (PWA)
- [ ] Real-time notifications
- [ ] Advanced analytics dashboard

### 📋 Planned Features
- [ ] Email templates customization
- [ ] Bulk operations
- [ ] API rate limiting
- [ ] Advanced search dan filtering
- [ ] Multi-language support
- [ ] Backup dan restore system

## Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

Untuk pertanyaan atau dukungan, silakan buat issue di repository ini atau hubungi tim development. 
