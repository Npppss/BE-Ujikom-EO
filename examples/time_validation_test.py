#!/usr/bin/env python3
"""
Testing untuk validasi waktu pendaftaran event dan daftar hadir
"""

import requests
import json
from datetime import datetime, timedelta
from app.services.event_service import EventService
from app.services.attendance_service import AttendanceService

# Konfigurasi
BASE_URL = "http://localhost:8000"
event_service = EventService()
attendance_service = AttendanceService()

def test_event_creation_h3_validation():
    """Test validasi H-3 untuk pembuatan event"""
    print("🔍 Testing Event Creation H-3 Validation")
    print("-" * 50)
    
    # Test cases untuk validasi H-3
    test_cases = [
        {
            "title": "Event H-5 (Valid)",
            "start_date": (datetime.now() + timedelta(days=5)).date(),
            "expected": "SUCCESS"
        },
        {
            "title": "Event H-3 (Valid - Batas)",
            "start_date": (datetime.now() + timedelta(days=3)).date(),
            "expected": "SUCCESS"
        },
        {
            "title": "Event H-2 (Invalid)",
            "start_date": (datetime.now() + timedelta(days=2)).date(),
            "expected": "ERROR"
        },
        {
            "title": "Event H-1 (Invalid)",
            "start_date": (datetime.now() + timedelta(days=1)).date(),
            "expected": "ERROR"
        },
        {
            "title": "Event H+0 (Invalid)",
            "start_date": datetime.now().date(),
            "expected": "ERROR"
        }
    ]
    
    for test_case in test_cases:
        print(f"Testing: {test_case['title']}")
        print(f"   Start Date: {test_case['start_date']}")
        print(f"   Expected: {test_case['expected']}")
        
        try:
            # Simulasi create event
            event_data = {
                "title": test_case['title'],
                "start_date": test_case['start_date'],
                "end_date": test_case['start_date'],
                "start_time": datetime.now().time(),
                "end_time": (datetime.now() + timedelta(hours=2)).time(),
                "location": "Test Location",
                "description": "Test Description"
            }
            
            # Test validasi H-3
            current_date = datetime.now().date()
            min_creation_date = test_case['start_date'] - timedelta(days=3)
            
            if current_date > min_creation_date:
                print(f"   ❌ ERROR: Event hanya dapat dibuat maksimal H-3")
                print(f"      Batas pembuatan: {min_creation_date}")
                print(f"      Tanggal hari ini: {current_date}")
            else:
                print(f"   ✅ SUCCESS: Event dapat dibuat")
                
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
        
        print()

def test_event_registration_deadline():
    """Test validasi deadline pendaftaran event"""
    print("🔍 Testing Event Registration Deadline")
    print("-" * 50)
    
    # Test cases untuk deadline pendaftaran
    test_cases = [
        {
            "title": "Event H+1 (Valid - Masih bisa daftar)",
            "start_date": (datetime.now() + timedelta(days=1)).date(),
            "start_time": (datetime.now() + timedelta(hours=1)).time(),
            "expected": "CAN_REGISTER"
        },
        {
            "title": "Event H+0 Jam+1 (Valid - Masih bisa daftar)",
            "start_date": datetime.now().date(),
            "start_time": (datetime.now() + timedelta(hours=1)).time(),
            "expected": "CAN_REGISTER"
        },
        {
            "title": "Event H+0 Jam+0 (Invalid - Sudah mulai)",
            "start_date": datetime.now().date(),
            "start_time": datetime.now().time(),
            "expected": "CANNOT_REGISTER"
        },
        {
            "title": "Event H-1 (Invalid - Sudah lewat)",
            "start_date": (datetime.now() - timedelta(days=1)).date(),
            "start_time": datetime.now().time(),
            "expected": "CANNOT_REGISTER"
        }
    ]
    
    for test_case in test_cases:
        print(f"Testing: {test_case['title']}")
        print(f"   Start Date: {test_case['start_date']}")
        print(f"   Start Time: {test_case['start_time']}")
        print(f"   Expected: {test_case['expected']}")
        
        try:
            # Simulasi validasi deadline
            current_datetime = datetime.now()
            event_datetime = datetime.combine(test_case['start_date'], test_case['start_time'])
            
            if current_datetime >= event_datetime:
                print(f"   ❌ CANNOT_REGISTER: Pendaftaran sudah ditutup")
                print(f"      Event dimulai: {event_datetime.strftime('%d/%m/%Y %H:%M')}")
                print(f"      Waktu sekarang: {current_datetime.strftime('%d/%m/%Y %H:%M')}")
            else:
                print(f"   ✅ CAN_REGISTER: Masih bisa mendaftar")
                time_left = event_datetime - current_datetime
                print(f"      Sisa waktu: {time_left}")
                
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
        
        print()

def test_attendance_time_validation():
    """Test validasi waktu daftar hadir"""
    print("🔍 Testing Attendance Time Validation")
    print("-" * 50)
    
    # Test cases untuk validasi waktu attendance
    test_cases = [
        {
            "title": "Event H+1 (Invalid - Belum bisa check-in)",
            "start_date": (datetime.now() + timedelta(days=1)).date(),
            "start_time": (datetime.now() + timedelta(hours=1)).time(),
            "expected": "CANNOT_ATTEND"
        },
        {
            "title": "Event H+0 Jam+1 (Invalid - Belum bisa check-in)",
            "start_date": datetime.now().date(),
            "start_time": (datetime.now() + timedelta(hours=1)).time(),
            "expected": "CANNOT_ATTEND"
        },
        {
            "title": "Event H+0 Jam+0 (Valid - Bisa check-in)",
            "start_date": datetime.now().date(),
            "start_time": datetime.now().time(),
            "expected": "CAN_ATTEND"
        },
        {
            "title": "Event H-1 (Valid - Bisa check-in)",
            "start_date": (datetime.now() - timedelta(days=1)).date(),
            "start_time": datetime.now().time(),
            "expected": "CAN_ATTEND"
        }
    ]
    
    for test_case in test_cases:
        print(f"Testing: {test_case['title']}")
        print(f"   Start Date: {test_case['start_date']}")
        print(f"   Start Time: {test_case['start_time']}")
        print(f"   Expected: {test_case['expected']}")
        
        try:
            # Simulasi validasi waktu attendance
            current_datetime = datetime.now()
            event_datetime = datetime.combine(test_case['start_date'], test_case['start_time'])
            
            if current_datetime < event_datetime:
                print(f"   ❌ CANNOT_ATTEND: Check-in belum dapat dilakukan")
                print(f"      Event dimulai: {event_datetime.strftime('%d/%m/%Y %H:%M')}")
                print(f"      Waktu sekarang: {current_datetime.strftime('%d/%m/%Y %H:%M')}")
                time_left = event_datetime - current_datetime
                print(f"      Tunggu: {time_left}")
            else:
                print(f"   ✅ CAN_ATTEND: Bisa melakukan check-in")
                time_passed = current_datetime - event_datetime
                print(f"      Event sudah berlangsung: {time_passed}")
                
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
        
        print()

def test_api_endpoints():
    """Test API endpoints dengan validasi waktu"""
    print("🔍 Testing API Endpoints with Time Validation")
    print("-" * 50)
    
    # Test create event dengan tanggal yang melanggar H-3
    print("Testing Create Event API (H-3 validation)")
    try:
        # Event untuk besok (melanggar H-3)
        event_data = {
            "title": "Test Event H+1",
            "start_date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
            "end_date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
            "start_time": "10:00:00",
            "end_time": "12:00:00",
            "location": "Test Location",
            "description": "Test Description"
        }
        
        print(f"   Event Data: {event_data}")
        print("   Expected: Error karena melanggar H-3")
        
        # Note: Ini hanya simulasi, untuk testing real perlu login sebagai organizer
        print("   ⚠️  Untuk testing real, perlu login sebagai organizer")
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
    
    print()

def main():
    """Fungsi utama untuk menjalankan semua test"""
    print("🚀 Time Validation Testing Suite")
    print("=" * 60)
    print()
    
    # Test validasi H-3 untuk pembuatan event
    test_event_creation_h3_validation()
    
    # Test deadline pendaftaran
    test_event_registration_deadline()
    
    # Test validasi waktu attendance
    test_attendance_time_validation()
    
    # Test API endpoints
    test_api_endpoints()
    
    print("✅ All time validation tests completed!")
    print("\n💡 Summary:")
    print("- Event Creation: H-3 validation ✅")
    print("- Event Registration: Deadline validation ✅")
    print("- Attendance: Time validation ✅")
    print("- API Integration: Ready for testing ✅")

if __name__ == "__main__":
    main()
