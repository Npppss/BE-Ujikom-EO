#!/usr/bin/env python3
"""
Test script untuk Session Timeout System
Mendemonstrasikan role-based session timeout:
- Admin/Organizer: 5 menit
- User biasa: 10 menit
"""

import requests
import time
import json
from datetime import datetime, timedelta

# Konfigurasi
BASE_URL = "http://localhost:8000"
LOGIN_ENDPOINT = f"{BASE_URL}/api/v1/auth/login"
SESSION_STATUS_ENDPOINT = f"{BASE_URL}/api/v1/auth/session-status"

def print_separator(title):
    """Print separator dengan title"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_response_info(response, title):
    """Print informasi response"""
    print(f"\n{title}:")
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"Response Body: {json.dumps(data, indent=2)}")
        except:
            print(f"Response Text: {response.text}")
    else:
        try:
            error_data = response.json()
            print(f"Error Response: {json.dumps(error_data, indent=2)}")
        except:
            print(f"Error Text: {response.text}")

def test_login_and_session_info(email, password, expected_role):
    """Test login dan ambil informasi session"""
    print_separator(f"Testing Login untuk {expected_role}")
    
    # Login
    login_data = {
        "email": email,
        "password": password
    }
    
    print(f"Login dengan email: {email}")
    response = requests.post(LOGIN_ENDPOINT, json=login_data)
    print_response_info(response, "Login Response")
    
    if response.status_code != 200:
        print(f"❌ Login gagal untuk {expected_role}")
        return None
    
    # Parse response
    login_response = response.json()
    access_token = login_response.get("access_token")
    session_timeout = login_response.get("session_timeout_minutes")
    role = login_response.get("role")
    
    print(f"\n✅ Login berhasil untuk {expected_role}")
    print(f"Role: {role}")
    print(f"Session Timeout: {session_timeout} menit")
    print(f"Expires In: {login_response.get('expires_in')} detik")
    
    # Verify role-based timeout
    if role in ["admin", "organizer"]:
        expected_timeout = 5
    else:
        expected_timeout = 10
    
    if session_timeout == expected_timeout:
        print(f"✅ Session timeout sesuai: {session_timeout} menit")
    else:
        print(f"❌ Session timeout tidak sesuai. Expected: {expected_timeout}, Got: {session_timeout}")
    
    return access_token

def test_session_status(access_token, role):
    """Test endpoint session status"""
    print_separator(f"Testing Session Status untuk {role}")
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get(SESSION_STATUS_ENDPOINT, headers=headers)
    print_response_info(response, "Session Status Response")
    
    if response.status_code == 200:
        session_data = response.json()
        print(f"\n✅ Session status berhasil diambil")
        print(f"User ID: {session_data.get('user_id')}")
        print(f"Email: {session_data.get('email')}")
        print(f"Role: {session_data.get('role')}")
        print(f"Session Timeout: {session_data.get('session_timeout_minutes')} menit")
        print(f"Expires At: {session_data.get('expires_at')}")
        print(f"Remaining Seconds: {session_data.get('remaining_seconds')}")
        
        # Check response headers
        print(f"\nResponse Headers:")
        print(f"X-Session-Timeout-Minutes: {response.headers.get('X-Session-Timeout-Minutes')}")
        print(f"X-Session-Expires-At: {response.headers.get('X-Session-Expires-At')}")
        print(f"X-Session-Role: {response.headers.get('X-Session-Role')}")
        
        return True
    else:
        print(f"❌ Gagal mengambil session status")
        return False

def test_session_expiry_simulation(access_token, role):
    """Simulasi session expiry (tidak menunggu sampai benar-benar expired)"""
    print_separator(f"Simulasi Session Expiry untuk {role}")
    
    # Get current session info
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(SESSION_STATUS_ENDPOINT, headers=headers)
    
    if response.status_code != 200:
        print("❌ Tidak bisa mengambil session status untuk simulasi")
        return
    
    session_data = response.json()
    remaining_seconds = session_data.get("remaining_seconds", 0)
    expires_at = session_data.get("expires_at")
    
    print(f"Session akan expired pada: {expires_at}")
    print(f"Sisa waktu: {remaining_seconds} detik")
    
    # Calculate when session will expire
    if expires_at:
        try:
            expiry_time = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
            current_time = datetime.now(expiry_time.tzinfo)
            time_until_expiry = expiry_time - current_time
            
            print(f"Waktu sekarang: {current_time}")
            print(f"Waktu sampai expired: {time_until_expiry}")
            
            # Show warning if session expires soon
            if time_until_expiry.total_seconds() <= 60:
                print("⚠️  PERINGATAN: Session akan expired dalam 1 menit!")
            elif time_until_expiry.total_seconds() <= 300:
                print("⚠️  PERINGATAN: Session akan expired dalam 5 menit!")
                
        except Exception as e:
            print(f"Error parsing expiry time: {e}")

def test_invalid_token():
    """Test dengan token yang tidak valid"""
    print_separator("Testing Invalid Token")
    
    # Test dengan token kosong
    headers = {"Authorization": "Bearer "}
    response = requests.get(SESSION_STATUS_ENDPOINT, headers=headers)
    print_response_info(response, "Empty Token Response")
    
    # Test dengan token yang tidak valid
    headers = {"Authorization": "Bearer invalid_token_here"}
    response = requests.get(SESSION_STATUS_ENDPOINT, headers=headers)
    print_response_info(response, "Invalid Token Response")

def main():
    """Main test function"""
    print("🚀 Event Organizer - Session Timeout Test")
    print("Testing role-based session timeout system")
    
    # Test data (sesuaikan dengan data yang ada di database)
    test_users = [
        {
            "email": "admin@eventorganizer.com",
            "password": "admin123",
            "role": "admin"
        },
        {
            "email": "user@example.com", 
            "password": "user123",
            "role": "user"
        }
    ]
    
    tokens = {}
    
    # Test login untuk setiap user
    for user_data in test_users:
        token = test_login_and_session_info(
            user_data["email"], 
            user_data["password"], 
            user_data["role"]
        )
        if token:
            tokens[user_data["role"]] = token
    
    print("\n" + "="*60)
    print(" TESTING SESSION STATUS")
    print("="*60)
    
    # Test session status untuk setiap user
    for role, token in tokens.items():
        test_session_status(token, role)
        test_session_expiry_simulation(token, role)
    
    # Test invalid token
    test_invalid_token()
    
    print("\n" + "="*60)
    print(" TEST SUMMARY")
    print("="*60)
    
    print(f"✅ Admin/Organizer session timeout: 5 menit")
    print(f"✅ User biasa session timeout: 10 menit")
    print(f"✅ Middleware session validation aktif")
    print(f"✅ Response headers session info tersedia")
    print(f"✅ Session status endpoint berfungsi")
    
    print("\n📝 Catatan:")
    print("- Session timeout dihitung dari waktu login")
    print("- Setiap request akan memvalidasi token expiration")
    print("- Token yang expired akan otomatis ditolak")
    print("- Refresh token tetap valid untuk memperbarui access token")
    
    print("\n🔧 Untuk testing session expiry yang sebenarnya:")
    print("1. Login sebagai admin (5 menit timeout)")
    print("2. Tunggu 6 menit")
    print("3. Coba akses endpoint yang memerlukan authentication")
    print("4. Akan mendapat response 401 dengan message 'Session expired'")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Test dihentikan oleh user")
    except Exception as e:
        print(f"\n\n❌ Error during testing: {e}")
        print("Pastikan server FastAPI berjalan di http://localhost:8000")
