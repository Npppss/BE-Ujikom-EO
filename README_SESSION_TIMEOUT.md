# Event Organizer - Session Timeout System

Sistem session timeout yang menerapkan durasi berbeda berdasarkan role user:
- **Admin dan User Management**: 5 menit
- **User Biasa**: 10 menit

## Fitur Utama

### 1. Role-Based Session Timeout
- **Admin/Organizer**: Session berakhir setelah 5 menit tidak ada aktivitas
- **User Biasa**: Session berakhir setelah 10 menit tidak ada aktivitas
- **Auto Logout**: Sistem otomatis logout user ketika session expired

### 2. Middleware Session Management
- **SessionTimeoutMiddleware**: Middleware yang memeriksa validitas token setiap request
- **Automatic Validation**: Validasi otomatis token expiration pada setiap endpoint
- **Response Headers**: Header response yang menunjukkan informasi session

### 3. API Endpoints
- **Session Status**: Endpoint untuk mengecek status session dan sisa waktu
- **Login Response**: Response login yang menyertakan informasi timeout

## Konfigurasi

### Environment Variables
```env
# Session timeout configuration
ADMIN_SESSION_TIMEOUT_MINUTES=5      # 5 menit untuk admin dan user management
USER_SESSION_TIMEOUT_MINUTES=10      # 10 menit untuk user biasa
```

### Default Values
```python
# Jika tidak diset di .env, akan menggunakan default:
ADMIN_SESSION_TIMEOUT_MINUTES = 5    # 5 menit
USER_SESSION_TIMEOUT_MINUTES = 10    # 10 menit
```

## Implementasi Teknis

### 1. Configuration (`app/core/config.py`)
```python
class Settings(BaseSettings):
    # Session timeout configuration for different roles
    ADMIN_SESSION_TIMEOUT_MINUTES: int = Field(default=5, alias="ADMIN_SESSION_TIMEOUT_MINUTES")
    USER_SESSION_TIMEOUT_MINUTES: int = Field(default=10, alias="USER_SESSION_TIMEOUT_MINUTES")
```

### 2. Security Module (`app/core/security.py`)
```python
def create_access_token(data: dict, expires_delta: timedelta = None, role: str = None):
    """
    Create access token with role-based expiration
    - Admin and user management roles: 5 minutes
    - Regular users: 10 minutes
    """
    if role and role in ["admin", "organizer"]:
        expire = datetime.utcnow() + timedelta(minutes=ADMIN_SESSION_TIMEOUT_MINUTES)
    else:
        expire = datetime.utcnow() + timedelta(minutes=USER_SESSION_TIMEOUT_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
```

### 3. Session Middleware (`app/middleware/session_middleware.py`)
```python
class SessionTimeoutMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Check for authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            response = await call_next(request)
            return response
        
        # Verify token and check expiration
        payload = verify_token(token, "access")
        if current_datetime >= exp_datetime:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "detail": "Session expired",
                    "code": "SESSION_EXPIRED",
                    "message": "Sesi Anda telah berakhir. Silakan login kembali."
                }
            )
```

### 4. Auth Service (`app/services/auth_service.py`)
```python
def login_user(self, db: Session, user: User) -> dict:
    # Create access token with role-based expiration
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role.name, "user_id": user.id},
        role=user.role.name
    )
    
    # Get session timeout based on role
    session_timeout_minutes = get_token_expiration_minutes(user.role.name)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": session_timeout_minutes * 60,
        "session_timeout_minutes": session_timeout_minutes,
        "role": user.role.name
    }
```

## API Endpoints

### 1. Login Response
```http
POST /api/v1/auth/login
```

**Response:**
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 300,
    "session_timeout_minutes": 5,
    "role": "admin"
}
```

### 2. Session Status
```http
GET /api/v1/auth/session-status
Authorization: Bearer <access_token>
```

**Response:**
```json
{
    "user_id": 1,
    "email": "admin@eventorganizer.com",
    "role": "admin",
    "session_timeout_minutes": 5,
    "expires_at": "2024-01-15T10:35:00",
    "remaining_seconds": 180,
    "is_active": true,
    "is_verified": true
}
```

### 3. Response Headers
Setiap response dari endpoint yang memerlukan authentication akan menyertakan header:
```
X-Session-Timeout-Minutes: 5
X-Session-Expires-At: 2024-01-15T10:35:00
X-Session-Role: admin
```

## Error Handling

### 1. Session Expired
```json
{
    "detail": "Session expired",
    "code": "SESSION_EXPIRED",
    "message": "Sesi Anda telah berakhir. Silakan login kembali."
}
```

### 2. Invalid Token
```json
{
    "detail": "Invalid token"
}
```

## Frontend Integration

### 1. JavaScript Timer
```javascript
// Set timer based on role
function setSessionTimer(role, expiresIn) {
    const timeoutMinutes = role === 'admin' || role === 'organizer' ? 5 : 10;
    const timeoutMs = timeoutMinutes * 60 * 1000;
    
    setTimeout(() => {
        // Auto logout when session expires
        localStorage.removeItem('access_token');
        window.location.href = '/login';
    }, timeoutMs);
}

// Check session status periodically
function checkSessionStatus() {
    fetch('/api/v1/auth/session-status', {
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.remaining_seconds <= 60) { // Warning 1 minute before
            showSessionWarning(data.remaining_seconds);
        }
    });
}
```

### 2. React Hook
```javascript
import { useEffect, useState } from 'react';

function useSessionTimeout(role) {
    const [remainingTime, setRemainingTime] = useState(null);
    
    useEffect(() => {
        const interval = setInterval(() => {
            // Check session status
            checkSessionStatus();
        }, 30000); // Check every 30 seconds
        
        return () => clearInterval(interval);
    }, [role]);
    
    return { remainingTime };
}
```

### 3. Vue.js Component
```vue
<template>
    <div class="session-warning" v-if="showWarning">
        <p>Sesi akan berakhir dalam {{ remainingMinutes }} menit</p>
        <button @click="extendSession">Perpanjang Sesi</button>
    </div>
</template>

<script>
export default {
    data() {
        return {
            showWarning: false,
            remainingMinutes: 0
        }
    },
    mounted() {
        this.startSessionTimer();
    },
    methods: {
        startSessionTimer() {
            setInterval(() => {
                this.checkSessionStatus();
            }, 30000);
        }
    }
}
</script>
```

## Testing

### 1. Test Session Expiry
```python
import time
import requests

# Login as admin
response = requests.post('/api/v1/auth/login', json={
    'email': 'admin@eventorganizer.com',
    'password': 'admin123'
})

token = response.json()['access_token']

# Wait for session to expire (6 minutes for admin)
time.sleep(360)

# Try to access protected endpoint
response = requests.get('/api/v1/auth/session-status', 
    headers={'Authorization': f'Bearer {token}'})

# Should return 401 with session expired message
assert response.status_code == 401
assert response.json()['code'] == 'SESSION_EXPIRED'
```

### 2. Test Role-Based Timeout
```python
# Login as regular user
response = requests.post('/api/v1/auth/login', json={
    'email': 'user@example.com',
    'password': 'user123'
})

user_token = response.json()['access_token']
user_timeout = response.json()['session_timeout_minutes']

# Login as admin
response = requests.post('/api/v1/auth/login', json={
    'email': 'admin@eventorganizer.com',
    'password': 'admin123'
})

admin_token = response.json()['access_token']
admin_timeout = response.json()['session_timeout_minutes']

# Verify different timeouts
assert user_timeout == 10  # Regular user: 10 minutes
assert admin_timeout == 5   # Admin: 5 minutes
```

## Security Considerations

### 1. Token Validation
- Setiap request akan memvalidasi token expiration
- Token yang expired akan langsung ditolak
- Refresh token tetap valid untuk memperbarui access token

### 2. Automatic Logout
- Frontend harus handle 401 response dengan code "SESSION_EXPIRED"
- Redirect user ke halaman login ketika session expired
- Clear semua data session dari localStorage/sessionStorage

### 3. Role-Based Security
- Admin dan organizer memiliki session yang lebih pendek untuk keamanan
- User biasa memiliki session yang lebih panjang untuk user experience
- Semua role tetap menggunakan refresh token untuk security

## Monitoring dan Logging

### 1. Session Events
```python
# Log session events
import logging

logger = logging.getLogger(__name__)

def log_session_event(user_id: int, role: str, event: str):
    logger.info(f"Session {event} for user {user_id} with role {role}")
    
# Usage in middleware
log_session_event(payload.get("user_id"), payload.get("role"), "expired")
```

### 2. Metrics
- Jumlah session expired per role
- Rata-rata durasi session per role
- Jumlah auto logout per hari

## Troubleshooting

### 1. Session Expired Too Quickly
- Periksa konfigurasi `ADMIN_SESSION_TIMEOUT_MINUTES` dan `USER_SESSION_TIMEOUT_MINUTES`
- Pastikan timezone server dan client sama
- Periksa apakah ada masalah dengan JWT token

### 2. Middleware Not Working
- Pastikan `SessionTimeoutMiddleware` sudah ditambahkan ke FastAPI app
- Periksa urutan middleware (session middleware harus setelah CORS)
- Periksa log untuk error pada middleware

### 3. Frontend Timer Issues
- Pastikan timer menggunakan `setInterval` bukan `setTimeout`
- Implementasikan error handling untuk network issues
- Gunakan `localStorage` untuk menyimpan token dengan aman
