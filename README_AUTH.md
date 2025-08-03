# Event Organizer - Authentication System

Sistem autentikasi lengkap untuk Event Organizer dengan fitur register, login, refresh token, forgot password, dan RBAC (Role-Based Access Control).

## Fitur yang Tersedia

### 1. Autentikasi Dasar
- **Register**: Pendaftaran user baru
- **Login**: Login dengan email dan password
- **Logout**: Logout dengan revoke refresh token

### 2. Token Management
- **Access Token**: JWT token dengan expiry 30 menit
- **Refresh Token**: JWT token dengan expiry 7 hari (wajib)
- **Token Refresh**: Endpoint untuk memperbarui access token

### 3. Password Management
- **Forgot Password**: Kirim email reset password
- **Reset Password**: Reset password menggunakan token
- **Change Password**: Ganti password untuk user yang sudah login

### 4. RBAC (Role-Based Access Control)
- **Roles**: admin, organizer, user
- **Permissions**: Granular permissions untuk setiap role
- **User Management**: CRUD operations untuk user dan role

## Setup dan Instalasi

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Konfigurasi Environment
Buat file `.env` dengan konfigurasi berikut:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/event_organizer

# Security Configuration
SECRET_KEY=your-secret-key-here-make-it-long-and-random
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email Configuration (for forgot password)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com

# Frontend URL (for password reset links)
FRONTEND_URL=http://localhost:3000
```

### 3. Inisialisasi Database
```bash
python -m app.db.init_db
```

Ini akan membuat:
- Tabel database yang diperlukan
- Default roles (admin, organizer, user)
- Admin user default (admin@eventorganizer.com / admin123)

### 4. Jalankan Aplikasi
```bash
uvicorn app.main:app --reload
```

## API Endpoints

### Authentication Endpoints

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

#### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### Refresh Token
```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Logout
```http
POST /api/v1/auth/logout
Content-Type: application/json

{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Forgot Password
```http
POST /api/v1/auth/forgot-password
Content-Type: application/json

{
  "email": "user@example.com"
}
```

#### Reset Password
```http
POST /api/v1/auth/reset-password
Content-Type: application/json

{
  "token": "reset-token-from-email",
  "new_password": "newpassword123"
}
```

#### Change Password
```http
POST /api/v1/auth/change-password
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "current_password": "oldpassword",
  "new_password": "newpassword123"
}
```

#### Get Current User
```http
GET /api/v1/auth/me
Authorization: Bearer <access_token>
```

### User Management Endpoints

#### Get All Users
```http
GET /api/v1/users/
Authorization: Bearer <access_token>
```

#### Get User by ID
```http
GET /api/v1/users/{user_id}
Authorization: Bearer <access_token>
```

#### Update User
```http
PUT /api/v1/users/{user_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "full_name": "Updated Name",
  "role_id": 2,
  "is_active": true
}
```

#### Delete User
```http
DELETE /api/v1/users/{user_id}
Authorization: Bearer <access_token>
```

### Role Management Endpoints

#### Get All Roles
```http
GET /api/v1/users/roles/
Authorization: Bearer <access_token>
```

#### Create Role
```http
POST /api/v1/users/roles/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "moderator",
  "description": "Moderator role",
  "permissions": ["event:read", "event:update"]
}
```

#### Update Role
```http
PUT /api/v1/users/roles/{role_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "updated_moderator",
  "description": "Updated moderator role",
  "permissions": ["event:read", "event:update", "user:read"]
}
```

#### Delete Role
```http
DELETE /api/v1/users/roles/{role_id}
Authorization: Bearer <access_token>
```

## Role dan Permission System

### Default Roles

#### 1. Admin
- **Permissions**: Full access to all features
- **Can**: Manage users, roles, events

#### 2. Organizer
- **Permissions**: Event management + user read
- **Can**: Create, update, delete events, view users

#### 3. User
- **Permissions**: Basic access
- **Can**: View events only

### Permission Format
Permissions menggunakan format `resource:action`:
- `user:read` - Read user data
- `user:create` - Create new users
- `user:update` - Update user data
- `user:delete` - Delete users
- `role:read` - Read role data
- `role:create` - Create new roles
- `role:update` - Update role data
- `role:delete` - Delete roles
- `event:read` - Read event data
- `event:create` - Create new events
- `event:update` - Update event data
- `event:delete` - Delete events

## Security Features

### 1. Password Security
- Password di-hash menggunakan bcrypt
- Minimum password strength validation
- Password reset dengan token yang expire

### 2. Token Security
- Access token expire dalam 30 menit
- Refresh token expire dalam 7 hari
- Token revocation saat logout/change password
- JWT dengan signature verification

### 3. RBAC Security
- Role-based access control
- Granular permissions
- Permission checking pada setiap endpoint

### 4. Email Security
- Password reset via email
- Token-based verification
- Secure email templates

## Error Handling

Sistem menggunakan HTTP status codes standar:
- `200` - Success
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

## Testing

### Test Register
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123","full_name":"Test User"}'
```

### Test Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

### Test Protected Endpoint
```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Production Considerations

### 1. Security
- Ganti SECRET_KEY dengan random string yang kuat
- Gunakan HTTPS di production
- Set up proper CORS configuration
- Implement rate limiting

### 2. Email Configuration
- Gunakan SMTP service yang reliable (SendGrid, AWS SES, etc.)
- Set up proper email templates
- Implement email verification

### 3. Database
- Gunakan connection pooling
- Set up database backups
- Implement proper indexing

### 4. Monitoring
- Set up logging
- Monitor token usage
- Track failed login attempts

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Periksa DATABASE_URL di .env
   - Pastikan database server running

2. **Email Not Sending**
   - Periksa SMTP configuration
   - Pastikan email credentials benar
   - Check firewall settings

3. **Token Expired**
   - Gunakan refresh token untuk mendapatkan access token baru
   - Pastikan waktu server benar

4. **Permission Denied**
   - Periksa role dan permissions user
   - Pastikan endpoint memerlukan permission yang tepat 