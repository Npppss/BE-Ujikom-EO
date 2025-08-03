# 🎪 Event Organizer Backend API

A comprehensive **FastAPI** backend system for event management with advanced features including authentication, QR code attendance, certificate management, and analytics.

## 🚀 Features

### 🔐 **Authentication & Authorization**
- **JWT-based authentication** with access & refresh tokens
- **Role-Based Access Control (RBAC)** - Admin, Organizer, User roles
- **Email verification** after registration
- **Password reset** functionality
- **Forgot password** with email recovery

### 📅 **Event Management**
- **Complete CRUD operations** for events
- **Event categories** (Business, Entertainment, Education, Technology, Health, Sports, Culture)
- **Event status** management (Draft, Published, Ongoing, Completed, Cancelled)
- **Rich event details** (location, pricing, capacity, media uploads)
- **Event analytics** and statistics
- **Featured events** and upcoming events lists

### 📱 **QR Code Attendance System**
- **Check-in/Check-out QR codes** for events
- **Real-time attendance tracking**
- **Attendance analytics** and reports
- **Universal QR scanner** endpoint

### 🎫 **Certificate Management**
- **Certificate generation** with custom templates
- **Bulk certificate creation** for all event participants
- **Certificate verification** system with unique codes
- **Template management** with file upload support
- **Certificate analytics** and statistics

### 📊 **Advanced Analytics**
- **Event performance metrics**
- **Attendance analytics**
- **Revenue tracking**
- **User engagement statistics**

## 🛠️ Technology Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy 2.0
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt
- **Email**: SMTP with python-multipart
- **QR Codes**: qrcode[pil] with Pillow
- **Validation**: Pydantic
- **Documentation**: Auto-generated OpenAPI/Swagger

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL 12+
- pip (Python package manager)

## 🚀 Quick Start

### 1. **Clone Repository**
```bash
git clone https://github.com/Npppss/BE-Ujikom-EO.git
cd BE-Ujikom-EO
```

### 2. **Setup Virtual Environment**
```bash
# Create virtual environment
python -m venv ujikom

# Activate virtual environment
# Windows:
ujikom\Scripts\activate
# Linux/Mac:
source ujikom/bin/activate
```

### 3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 4. **Environment Configuration**
Create a `.env` file in the root directory:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/event_organizer_db

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com

# Frontend URL (for email links)
FRONTEND_URL=http://localhost:3000
```

### 5. **Database Setup**
```bash
# Reset database (if needed)
python reset_db.py

# Initialize database with default data
python -m app.db.init_db
```

### 6. **Run Application**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📚 API Documentation

Once the server is running, you can access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🔑 Default Credentials

After running `init_db.py`, these default users are created:

### **Admin User**
- **Email**: `admin@eventorganizer.com`
- **Password**: `admin123`
- **Role**: Admin (full access)

### **Organizer User**
- **Email**: `organizer@eventorganizer.com`
- **Password**: `organizer123`
- **Role**: Organizer (event management)

## 📖 API Endpoints

### 🔐 **Authentication**
```
POST /auth/register          # Register new user
POST /auth/login            # Login user
POST /auth/refresh          # Refresh access token
POST /auth/logout           # Logout user
POST /auth/forgot-password  # Request password reset
POST /auth/reset-password   # Reset password
POST /auth/verify-email     # Verify email address
POST /auth/resend-verification # Resend verification email
GET  /auth/me               # Get current user info
```

### 👥 **User Management**
```
GET    /users/              # Get all users (admin only)
GET    /users/{user_id}     # Get user by ID
PUT    /users/{user_id}     # Update user
DELETE /users/{user_id}     # Delete user
GET    /users/roles/        # Get all roles
POST   /users/roles/        # Create role
PUT    /users/roles/{id}    # Update role
DELETE /users/roles/{id}    # Delete role
```

### 📅 **Event Management**
```
POST   /events/                    # Create event
GET    /events/                    # Get all events (with filters)
GET    /events/{event_id}          # Get event by ID
PUT    /events/{event_id}          # Update event
DELETE /events/{event_id}          # Delete event
POST   /events/{event_id}/publish  # Publish event
POST   /events/{event_id}/like     # Like event
DELETE /events/{event_id}/like     # Unlike event
POST   /events/{event_id}/register # Register for event
GET    /events/analytics/stats     # Global event statistics
GET    /events/featured/list       # Featured events
GET    /events/upcoming/list       # Upcoming events
```

### 📱 **Attendance System**
```
POST   /attendance/{event_id}/start-check-in    # Start check-in
POST   /attendance/{event_id}/stop-check-in     # Stop check-in
POST   /attendance/{event_id}/start-check-out   # Start check-out
POST   /attendance/{event_id}/stop-check-out    # Stop check-out
GET    /attendance/{event_id}/check-in-qr       # Get check-in QR
GET    /attendance/{event_id}/check-out-qr      # Get check-out QR
POST   /attendance/scan-check-in                # Scan check-in QR
POST   /attendance/scan-check-out               # Scan check-out QR
POST   /attendance/scan-qr                      # Universal QR scanner
GET    /attendance/{event_id}/list              # Get event attendance
GET    /attendance/{event_id}/summary           # Attendance summary
GET    /attendance/my-attendance                # User's attendance
```

### 🎫 **Certificate Management**
```
POST   /certificates/                           # Create certificate
GET    /certificates/                           # Get all certificates
GET    /certificates/{id}                       # Get certificate by ID
PUT    /certificates/{id}                       # Update certificate
DELETE /certificates/{id}                       # Delete certificate
POST   /certificates/{id}/issue                 # Issue certificate
POST   /certificates/{id}/generate              # Generate certificate PDF
POST   /certificates/bulk-generate              # Bulk generate certificates
POST   /certificates/verify                     # Verify certificate
POST   /certificates/templates/                 # Create template
GET    /certificates/templates/                 # Get all templates
PUT    /certificates/templates/{id}             # Update template
DELETE /certificates/templates/{id}             # Delete template
POST   /certificates/upload-template            # Upload template file
GET    /certificates/stats/overview             # Certificate statistics
GET    /certificates/my-certificates            # User's certificates
```

## 🗄️ Database Schema

### **Core Tables**
- `users` - User accounts and profiles
- `roles` - User roles and permissions
- `refresh_tokens` - JWT refresh tokens
- `password_reset_tokens` - Password reset functionality

### **Event Management**
- `events` - Event information and details
- `event_registrations` - Event registrations
- `event_likes` - Event likes/reactions
- `event_comments` - Event comments

### **Attendance System**
- `attendances` - Attendance records with check-in/out times

### **Certificate System**
- `certificates` - Certificate records and metadata
- `certificate_templates` - Certificate templates
- `certificate_verifications` - Certificate verification logs

## 🔧 Development

### **Project Structure**
```
event_organizer_backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/
│   │           ├── auth.py
│   │           ├── user.py
│   │           ├── event.py
│   │           ├── attendance.py
│   │           └── certificate.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── dependencies.py
│   ├── db/
│   │   ├── database.py
│   │   ├── init_db.py
│   │   └── models/
│   │       ├── models.py
│   │       ├── event.py
│   │       └── certificate.py
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── event.py
│   │   ├── attendance.py
│   │   └── certificate.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── event_service.py
│   │   ├── attendance_service.py
│   │   ├── certificate_service.py
│   │   ├── email_service.py
│   │   └── qr_service.py
│   └── main.py
├── uploads/
├── requirements.txt
├── reset_db.py
├── generate_secret.py
└── README.md
```

### **Running Tests**
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

### **Database Migrations**
```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head
```

## 🚀 Deployment

### **Production Setup**
1. Set `ENVIRONMENT=production` in `.env`
2. Use production database (PostgreSQL)
3. Configure proper SMTP settings
4. Set secure `SECRET_KEY`
5. Use reverse proxy (nginx) with SSL

### **Docker Deployment**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the [API Documentation](http://localhost:8000/docs)
2. Review the [Issues](https://github.com/Npppss/BE-Ujikom-EO/issues)
3. Create a new issue with detailed information

## 🎯 Roadmap

- [ ] **Ticket Management System**
- [ ] **Payment Gateway Integration**
- [ ] **Push Notification System**
- [ ] **Real-time Dashboard**
- [ ] **Event Page Builder**
- [ ] **Virtual & Hybrid Events**
- [ ] **Sponsor Management**
- [ ] **Advanced Analytics**
- [ ] **Automation & Workflows**
- [ ] **Internationalization**

---

**Made for Event Organizers**

*Built with FastAPI, PostgreSQL, and modern Python practices* 