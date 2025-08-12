#!/usr/bin/env python3
"""
Contoh testing untuk fitur validasi password dengan regex
"""

import requests
import json
from app.core.password_validator import password_validator

# Konfigurasi
BASE_URL = "http://localhost:8000"

def test_password_requirements():
    """Test endpoint untuk mendapatkan requirement password"""
    print("🔍 Testing Password Requirements Endpoint")
    print("-" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/auth/password-requirements")
        if response.status_code == 200:
            data = response.json()
            print("✅ Password Requirements:")
            print(f"   Minimal Length: {data['min_length']}")
            print("   Requirements:")
            for req in data['requirements']:
                print(f"   - {req}")
            print(f"   Example: {data['example']}")
        else:
            print(f"❌ Failed to get requirements: {response.text}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print()

def test_password_validation_api():
    """Test endpoint untuk validasi password"""
    print("🔍 Testing Password Validation API")
    print("-" * 50)
    
    # Test cases
    test_passwords = [
        # Valid passwords
        "Password123#",
        "MySecurePass1!",
        "EventOrganizer2024@",
        "Admin@123",
        "User#456",
        
        # Invalid passwords
        "password",  # no uppercase, no digit, no special
        "123456",    # no letters, no special
        "qwerty",    # no uppercase, no digit, no special
        "Password",  # no digit, no special
        "password123",  # no uppercase, no special
        "PASSWORD123",  # no lowercase, no special
        "Pass123",   # too short, no special
        "Password!", # no digit
        "pass123!",  # no uppercase
        "PASS123!",  # no lowercase
    ]
    
    for password in test_passwords:
        print(f"Testing password: '{password}'")
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/auth/validate-password",
                json={"password": password}
            )
            
            if response.status_code == 200:
                data = response.json()
                status = "✅ VALID" if data['is_valid'] else "❌ INVALID"
                strength = data['strength'].upper()
                common = "⚠️ COMMON" if data['is_common_password'] else ""
                
                print(f"   Status: {status}")
                print(f"   Strength: {strength}")
                if data['is_common_password']:
                    print(f"   Warning: {common}")
                
                if not data['is_valid']:
                    print("   Errors:")
                    for error in data['errors']:
                        print(f"   - {error}")
            else:
                print(f"   ❌ API Error: {response.text}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        print()

def test_direct_validator():
    """Test password validator secara langsung"""
    print("🔍 Testing Direct Password Validator")
    print("-" * 50)
    
    test_passwords = [
        "Password123#",
        "weak",
        "password",
        "MySecurePass1!",
        "123456"
    ]
    
    for password in test_passwords:
        print(f"Testing: '{password}'")
        
        # Test validation
        is_valid, errors = password_validator.validate_password(password)
        print(f"   Valid: {is_valid}")
        
        if not is_valid:
            print("   Errors:")
            for error in errors:
                print(f"   - {error}")
        
        # Test strength
        strength = password_validator.get_password_strength(password)
        print(f"   Strength: {strength}")
        
        # Test common password
        is_common = password_validator.is_common_password(password)
        if is_common:
            print("   ⚠️ Common password detected!")
        
        print()

def test_regex_patterns():
    """Test regex patterns secara individual"""
    print("🔍 Testing Regex Patterns")
    print("-" * 50)
    
    test_cases = [
        ("Length Test", "short", "longpassword"),
        ("Uppercase Test", "lowercase", "Uppercase"),
        ("Lowercase Test", "UPPERCASE", "Lowercase"),
        ("Digit Test", "nodigits", "with123"),
        ("Special Test", "nospecial", "with@#$")
    ]
    
    for test_name, invalid, valid in test_cases:
        print(f"{test_name}:")
        print(f"   Invalid: '{invalid}'")
        print(f"   Valid: '{valid}'")
        print()

def test_registration_with_validation():
    """Test registrasi dengan password validation"""
    print("🔍 Testing Registration with Password Validation")
    print("-" * 50)
    
    test_users = [
        {
            "email": "test1@example.com",
            "password": "ValidPass123!",
            "full_name": "Test User 1"
        },
        {
            "email": "test2@example.com", 
            "password": "weak",
            "full_name": "Test User 2"
        },
        {
            "email": "test3@example.com",
            "password": "password",
            "full_name": "Test User 3"
        }
    ]
    
    for i, user_data in enumerate(test_users, 1):
        print(f"Test {i}: Registering user with password '{user_data['password']}'")
        try:
            response = requests.post(
                f"{BASE_URL}/api/v1/auth/register",
                json=user_data
            )
            
            if response.status_code == 200:
                print("   ✅ Registration successful")
            else:
                error_data = response.json()
                print(f"   ❌ Registration failed: {error_data.get('detail', 'Unknown error')}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        print()

def main():
    """Fungsi utama untuk menjalankan semua test"""
    print("🚀 Password Validation Testing Suite")
    print("=" * 60)
    print()
    
    # Test password requirements
    test_password_requirements()
    
    # Test password validation API
    test_password_validation_api()
    
    # Test direct validator
    test_direct_validator()
    
    # Test regex patterns
    test_regex_patterns()
    
    # Test registration with validation
    test_registration_with_validation()
    
    print("✅ All tests completed!")
    print("\n💡 Tips:")
    print("- Pastikan server berjalan di http://localhost:8000")
    print("- Password yang kuat: minimal 8 karakter, huruf besar/kecil, angka, dan karakter spesial")
    print("- Contoh password yang valid: Password123#, MySecurePass1!, Admin@123")

if __name__ == "__main__":
    main()
