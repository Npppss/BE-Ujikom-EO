# Event Organizer - Email Verification System

Sistem verifikasi email lengkap untuk Event Organizer yang memastikan keamanan dan validitas akun pengguna.

## Fitur yang Tersedia

### 1. Email Verification Flow
- **Automatic Verification Email**: Email verifikasi otomatis saat registrasi
- **Token-based Verification**: Verifikasi menggunakan token yang aman
- **24-hour Expiry**: Token verifikasi expire dalam 24 jam
- **Resend Verification**: Kemampuan untuk kirim ulang email verifikasi

### 2. Security Features
- **Email Validation**: Validasi format email
- **Token Security**: Token unik dan random untuk setiap user
- **Expiry Protection**: Token expire otomatis untuk keamanan
- **Duplicate Prevention**: Mencegah verifikasi ganda

### 3. User Experience
- **Clear Instructions**: Email dengan instruksi yang jelas
- **Welcome Email**: Email selamat datang setelah verifikasi
- **Error Handling**: Pesan error yang informatif
- **Resend Option**: Opsi untuk kirim ulang email verifikasi

## Setup dan Instalasi

### 1. Konfigurasi Email
Pastikan konfigurasi email di file `.env` sudah benar:

```env
# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com
FRONTEND_URL=http://localhost:3000
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

### Registration dengan Email Verification

#### Register User
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "John Doe"
}
```

Response:
```json
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "user",
  "is_active": true,
  "is_verified": false,
  "created_at": "2024-01-01T10:00:00"
}
```

**Note**: User akan menerima email verifikasi otomatis setelah registrasi.

#### Verify Email
```http
POST /api/v1/auth/verify-email
Content-Type: application/json

{
  "token": "verification-token-from-email"
}
```

Response:
```json
{
  "message": "Email verified successfully. You can now log in."
}
```

#### Resend Verification Email
```http
POST /api/v1/auth/resend-verification
Content-Type: application/json

{
  "email": "user@example.com"
}
```

Response:
```json
{
  "message": "Verification email sent successfully"
}
```

### Login dengan Email Verification

#### Login (Email harus terverifikasi)
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**Jika email belum terverifikasi:**
```json
{
  "detail": "Please verify your email before logging in"
}
```

**Jika email sudah terverifikasi:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

## Workflow Email Verification

### 1. Registration Process
1. **User Register**: User mendaftar dengan email dan password
2. **Account Created**: Akun dibuat dengan status `is_verified = false`
3. **Verification Token**: Token verifikasi unik dibuat
4. **Email Sent**: Email verifikasi dikirim otomatis
5. **User Informed**: User mendapat pesan untuk cek email

### 2. Email Verification Process
1. **User Receives Email**: User menerima email verifikasi
2. **Click Link**: User klik link verifikasi di email
3. **Token Validation**: Sistem validasi token
4. **Account Verified**: Status `is_verified` diubah ke `true`
5. **Welcome Email**: Email selamat datang dikirim
6. **Can Login**: User sekarang bisa login

### 3. Resend Verification Process
1. **User Requests**: User request kirim ulang email verifikasi
2. **New Token**: Token verifikasi baru dibuat
3. **Email Sent**: Email verifikasi baru dikirim
4. **Old Token Invalidated**: Token lama tidak valid lagi

## Email Templates

### Email Verification Template
```html
<h2>Email Verification</h2>
<p>Hello [User Name],</p>
<p>Thank you for registering with Event Organizer. Please verify your email address to complete your registration.</p>
<p>Click the link below to verify your email:</p>
<p><a href="[VERIFICATION_URL]">Verify Email</a></p>
<p>If the button doesn't work, copy and paste this link into your browser:</p>
<p>[VERIFICATION_URL]</p>
<p>This verification link will expire in 24 hours for security reasons.</p>
<p>If you didn't create an account with Event Organizer, please ignore this email.</p>
```

### Welcome Email Template (Setelah Verifikasi)
```html
<h2>Welcome to Event Organizer!</h2>
<p>Hello [User Name],</p>
<p>Thank you for registering with Event Organizer. Your account has been created successfully!</p>
<p>You can now log in to your account and start organizing amazing events.</p>
```

## Database Schema

### User Table (Updated)
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    email_verification_token VARCHAR(500) UNIQUE,
    email_verification_expires TIMESTAMP,
    role_id INTEGER REFERENCES roles(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP
);
```

## Security Features

### 1. Token Security
- **Random Generation**: Token dibuat menggunakan `secrets.token_urlsafe(32)`
- **Unique Tokens**: Setiap user memiliki token unik
- **24-hour Expiry**: Token expire dalam 24 jam
- **One-time Use**: Token hanya bisa digunakan sekali

### 2. Email Security
- **SMTP Authentication**: Menggunakan SMTP dengan authentication
- **TLS Encryption**: Email dikirim menggunakan TLS
- **HTML Sanitization**: Email content di-sanitize untuk keamanan

### 3. Account Security
- **Verification Required**: User harus verifikasi email sebelum login
- **Token Invalidation**: Token dihapus setelah verifikasi berhasil
- **Duplicate Prevention**: Mencegah verifikasi ganda

## Error Handling

### Common Error Messages

#### Invalid Token
```json
{
  "detail": "Invalid or expired verification token"
}
```

#### Email Already Verified
```json
{
  "detail": "Email is already verified"
}
```

#### Email Not Verified (Login)
```json
{
  "detail": "Please verify your email before logging in"
}
```

#### Email Not Found (Resend)
```json
{
  "message": "Verification email sent successfully"
}
```
*Note: Tidak mengungkapkan apakah email ada atau tidak untuk keamanan*

## Testing

### Test Registration Flow
```bash
# 1. Register user
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","full_name":"Test User"}'

# 2. Try to login (should fail)
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# 3. Verify email (use token from email)
curl -X POST "http://localhost:8000/api/v1/auth/verify-email" \
  -H "Content-Type: application/json" \
  -d '{"token":"TOKEN_FROM_EMAIL"}'

# 4. Login again (should succeed)
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

### Test Resend Verification
```bash
# Resend verification email
curl -X POST "http://localhost:8000/api/v1/auth/resend-verification" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com"}'
```

## Frontend Integration

### React/Next.js Example
```javascript
// Registration component
const registerUser = async (userData) => {
  try {
    const response = await fetch('/api/v1/auth/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData)
    });
    
    if (response.ok) {
      // Show message to check email
      alert('Registration successful! Please check your email to verify your account.');
    }
  } catch (error) {
    console.error('Registration failed:', error);
  }
};

// Email verification component
const verifyEmail = async (token) => {
  try {
    const response = await fetch('/api/v1/auth/verify-email', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ token })
    });
    
    if (response.ok) {
      alert('Email verified successfully! You can now log in.');
      // Redirect to login page
    }
  } catch (error) {
    console.error('Verification failed:', error);
  }
};

// Resend verification component
const resendVerification = async (email) => {
  try {
    const response = await fetch('/api/v1/auth/resend-verification', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email })
    });
    
    if (response.ok) {
      alert('Verification email sent successfully!');
    }
  } catch (error) {
    console.error('Resend failed:', error);
  }
};
```

## Production Considerations

### 1. Email Service
- **Use Professional SMTP**: Gunakan SendGrid, AWS SES, atau Mailgun
- **Email Templates**: Gunakan template service untuk email yang profesional
- **Email Monitoring**: Monitor delivery rates dan bounce rates

### 2. Security
- **HTTPS**: Pastikan semua komunikasi menggunakan HTTPS
- **Rate Limiting**: Batasi request untuk resend verification
- **Token Rotation**: Rotate verification tokens secara berkala

### 3. User Experience
- **Clear Instructions**: Berikan instruksi yang jelas di email
- **Mobile Responsive**: Email template harus responsive
- **Fallback Options**: Berikan opsi manual jika link tidak berfungsi

### 4. Monitoring
- **Email Delivery**: Monitor email delivery success rates
- **Verification Rates**: Track berapa user yang berhasil verifikasi
- **Error Logging**: Log semua error untuk debugging

## Troubleshooting

### Common Issues

1. **Email Not Received**
   - Periksa spam folder
   - Verifikasi SMTP configuration
   - Check email delivery logs

2. **Token Expired**
   - Gunakan resend verification endpoint
   - Token expire dalam 24 jam

3. **Invalid Token**
   - Pastikan token di-copy dengan benar
   - Token hanya bisa digunakan sekali

4. **SMTP Errors**
   - Periksa SMTP credentials
   - Pastikan port dan server benar
   - Check firewall settings 