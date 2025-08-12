# Event Organizer - Password Validation System

Sistem validasi password yang kuat menggunakan regex patterns untuk memastikan keamanan password sesuai dengan requirement yang ditentukan.

## Fitur Validasi Password

### 1. **Requirement Password Strength**
Password harus memenuhi kriteria berikut:
- **Minimal 8 karakter**
- **Mengandung minimal 1 huruf besar (A-Z)**
- **Mengandung minimal 1 huruf kecil (a-z)**
- **Mengandung minimal 1 angka (0-9)**
- **Mengandung minimal 1 karakter spesial (!@#$%^&*()_+-=[]{}|;:,.<>?)**

### 2. **Regex Patterns yang Digunakan**
```python
patterns = {
    'length': r'.{8,}',  # Minimal 8 karakter
    'uppercase': r'[A-Z]',  # Huruf besar
    'lowercase': r'[a-z]',  # Huruf kecil
    'digit': r'\d',  # Angka
    'special': r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]'  # Karakter spesial
}
```

### 3. **Password Strength Levels**
- **Weak**: ≤ 2 kriteria terpenuhi
- **Medium**: 3 kriteria terpenuhi
- **Strong**: 4 kriteria terpenuhi
- **Very Strong**: 5 kriteria terpenuhi

### 4. **Common Password Detection**
Sistem mendeteksi password umum yang mudah ditebak seperti:
- `password`, `123456`, `qwerty`
- `admin`, `admin123`, `letmein`
- `test`, `guest`, `demo`
- Dan 40+ password umum lainnya

## API Endpoints

### 1. **Get Password Requirements**
```http
GET /api/v1/auth/password-requirements
```

**Response:**
```json
{
  "min_length": 8,
  "requirements": [
    "Minimal 8 karakter",
    "Minimal 1 huruf besar (A-Z)",
    "Minimal 1 huruf kecil (a-z)",
    "Minimal 1 angka (0-9)",
    "Minimal 1 karakter spesial (!@#$%^&*()_+-=[]{}|;:,.<>?)"
  ],
  "example": "Password123#"
}
```

### 2. **Validate Password Strength**
```http
POST /api/v1/auth/validate-password
Content-Type: application/json

{
  "password": "MyPassword123!"
}
```

**Response:**
```json
{
  "is_valid": true,
  "errors": [],
  "strength": "very_strong",
  "is_common_password": false,
  "requirements": {
    "min_length": 8,
    "requirements": [
      "Minimal 8 karakter",
      "Minimal 1 huruf besar (A-Z)",
      "Minimal 1 huruf kecil (a-z)",
      "Minimal 1 angka (0-9)",
      "Minimal 1 karakter spesial (!@#$%^&*()_+-=[]{}|;:,.<>?)"
    ],
    "example": "Password123#"
  }
}
```

**Error Response Example:**
```json
{
  "is_valid": false,
  "errors": [
    "Password harus minimal 8 karakter",
    "Password harus mengandung minimal 1 huruf besar",
    "Password harus mengandung minimal 1 karakter spesial (!@#$%^&*()_+-=[]{}|;:,.<>?)"
  ],
  "strength": "weak",
  "is_common_password": false,
  "requirements": {
    "min_length": 8,
    "requirements": [
      "Minimal 8 karakter",
      "Minimal 1 huruf besar (A-Z)",
      "Minimal 1 huruf kecil (a-z)",
      "Minimal 1 angka (0-9)",
      "Minimal 1 karakter spesial (!@#$%^&*()_+-=[]{}|;:,.<>?)"
    ],
    "example": "Password123#"
  }
}
```

## Implementasi di Frontend

### 1. **Real-time Password Validation**
```javascript
// Contoh implementasi di React
const [password, setPassword] = useState('');
const [passwordValidation, setPasswordValidation] = useState(null);

const validatePassword = async (password) => {
  try {
    const response = await fetch('/api/v1/auth/validate-password', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ password })
    });
    
    const result = await response.json();
    setPasswordValidation(result);
  } catch (error) {
    console.error('Password validation failed:', error);
  }
};

// Gunakan di input password
<input
  type="password"
  value={password}
  onChange={(e) => {
    setPassword(e.target.value);
    validatePassword(e.target.value);
  }}
/>
```

### 2. **Password Strength Indicator**
```jsx
const PasswordStrengthIndicator = ({ validation }) => {
  if (!validation) return null;
  
  const getStrengthColor = (strength) => {
    switch (strength) {
      case 'weak': return 'red';
      case 'medium': return 'orange';
      case 'strong': return 'yellow';
      case 'very_strong': return 'green';
      default: return 'gray';
    }
  };
  
  return (
    <div className="password-strength">
      <div className="strength-bar">
        <div 
          className="strength-fill"
          style={{ 
            backgroundColor: getStrengthColor(validation.strength),
            width: validation.is_valid ? '100%' : '25%'
          }}
        />
      </div>
      <span className="strength-text">
        Strength: {validation.strength.replace('_', ' ')}
      </span>
    </div>
  );
};
```

### 3. **Password Requirements Display**
```jsx
const PasswordRequirements = ({ validation }) => {
  if (!validation) return null;
  
  return (
    <div className="password-requirements">
      <h4>Password Requirements:</h4>
      <ul>
        {validation.requirements.requirements.map((req, index) => (
          <li key={index} className="requirement-item">
            {req}
          </li>
        ))}
      </ul>
      {validation.is_common_password && (
        <div className="warning">
          ⚠️ Password terlalu umum dan mudah ditebak
        </div>
      )}
    </div>
  );
};
```

## Contoh Password yang Valid

### ✅ **Password yang Memenuhi Semua Kriteria:**
- `Password123#`
- `MySecurePass1!`
- `EventOrganizer2024@`
- `Admin@123`
- `User#456`

### ❌ **Password yang Tidak Valid:**
- `password` (tidak ada huruf besar, angka, karakter spesial)
- `123456` (tidak ada huruf, karakter spesial)
- `qwerty` (tidak ada huruf besar, angka, karakter spesial)
- `Password` (tidak ada angka, karakter spesial)
- `password123` (tidak ada huruf besar, karakter spesial)

## Integrasi dengan Endpoint Lain

### 1. **Register User**
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "MySecurePass1!",
  "full_name": "John Doe"
}
```

**Error Response jika Password Tidak Valid:**
```json
{
  "detail": "Password tidak memenuhi requirement: Password harus minimal 8 karakter; Password harus mengandung minimal 1 huruf besar; Password harus mengandung minimal 1 karakter spesial (!@#$%^&*()_+-=[]{}|;:,.<>?)"
}
```

### 2. **Reset Password**
```http
POST /api/v1/auth/reset-password
Content-Type: application/json

{
  "token": "reset_token_here",
  "new_password": "NewSecurePass1!"
}
```

### 3. **Change Password**
```http
POST /api/v1/auth/change-password
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "current_password": "OldPassword123!",
  "new_password": "NewPassword456@"
}
```

## Security Features

### 1. **Regex Pattern Security**
- Patterns yang digunakan aman dan tidak rentan terhadap ReDoS attacks
- Karakter spesial yang diizinkan terbatas dan aman
- Tidak ada pattern yang bisa menyebabkan infinite loops

### 2. **Common Password Detection**
- Database password umum yang terus diperbarui
- Deteksi password yang mudah ditebak
- Mencegah penggunaan password yang umum

### 3. **Real-time Validation**
- Validasi real-time di frontend
- Feedback langsung ke user
- Mencegah submit form dengan password lemah

## Testing

### 1. **Unit Tests**
```python
def test_password_validation():
    # Test valid password
    is_valid, errors = password_validator.validate_password("Password123#")
    assert is_valid == True
    assert len(errors) == 0
    
    # Test invalid password
    is_valid, errors = password_validator.validate_password("weak")
    assert is_valid == False
    assert len(errors) > 0
    
    # Test common password
    is_common = password_validator.is_common_password("password")
    assert is_common == True
```

### 2. **Integration Tests**
```python
def test_password_validation_endpoint():
    response = client.post("/api/v1/auth/validate-password", 
                          json={"password": "Password123#"})
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] == True
    assert data["strength"] == "very_strong"
```

## Performance Considerations

### 1. **Regex Optimization**
- Patterns yang digunakan sudah dioptimasi
- Tidak ada nested quantifiers yang bisa menyebabkan backtracking
- Validasi dilakukan secara berurutan untuk efisiensi

### 2. **Caching**
- Password requirements di-cache untuk mengurangi overhead
- Common password list di-cache dalam memory

### 3. **Frontend Validation**
- Validasi real-time di frontend untuk UX yang lebih baik
- Backend validation sebagai fallback untuk keamanan

## Error Handling

### 1. **Validation Errors**
- Error messages yang jelas dan informatif
- Multiple errors ditampilkan sekaligus
- Saran perbaikan untuk user

### 2. **API Errors**
- HTTP 400 untuk password yang tidak valid
- Error messages yang konsisten
- Proper error codes untuk debugging

## Best Practices

### 1. **User Experience**
- Tampilkan requirement password di form registrasi
- Real-time feedback saat user mengetik password
- Visual indicator untuk password strength

### 2. **Security**
- Jangan tampilkan password di logs
- Hash password sebelum disimpan ke database
- Rate limiting untuk endpoint validation

### 3. **Maintenance**
- Update common password list secara berkala
- Monitor password patterns yang sering digunakan
- Review dan update regex patterns jika diperlukan

---

**Password Validation System Ready for Production Use**
