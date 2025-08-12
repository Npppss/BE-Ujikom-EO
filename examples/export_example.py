#!/usr/bin/env python3
"""
Contoh penggunaan fitur ekspor data Event Organizer
"""

import requests
import json
import os
from datetime import datetime

# Konfigurasi
BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@eventorganizer.com"
ADMIN_PASSWORD = "admin123"

def login_user(email: str, password: str) -> str:
    """Login user dan dapatkan access token"""
    url = f"{BASE_URL}/api/v1/auth/login"
    data = {
        "email": email,
        "password": password
    }
    
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Login failed: {response.text}")

def export_statistics_excel(access_token: str) -> bool:
    """Ekspor statistik ke Excel"""
    url = f"{BASE_URL}/api/v1/export/statistics/excel"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        # Simpan file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"statistik_kegiatan_{timestamp}.xlsx"
        
        with open(filename, "wb") as f:
            f.write(response.content)
        
        print(f"✅ Statistik berhasil diekspor ke: {filename}")
        return True
    else:
        print(f"❌ Gagal ekspor statistik: {response.text}")
        return False

def export_statistics_csv(access_token: str) -> bool:
    """Ekspor statistik ke CSV"""
    url = f"{BASE_URL}/api/v1/export/statistics/csv"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        # Simpan file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"statistik_kegiatan_{timestamp}.csv"
        
        with open(filename, "wb") as f:
            f.write(response.content)
        
        print(f"✅ Statistik berhasil diekspor ke: {filename}")
        return True
    else:
        print(f"❌ Gagal ekspor statistik: {response.text}")
        return False

def export_participants_excel(access_token: str, event_id: int = None) -> bool:
    """Ekspor data peserta ke Excel"""
    url = f"{BASE_URL}/api/v1/export/participants/excel"
    if event_id:
        url += f"?event_id={event_id}"
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        # Simpan file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if event_id:
            filename = f"data_peserta_event_{event_id}_{timestamp}.xlsx"
        else:
            filename = f"data_peserta_semua_{timestamp}.xlsx"
        
        with open(filename, "wb") as f:
            f.write(response.content)
        
        print(f"✅ Data peserta berhasil diekspor ke: {filename}")
        return True
    else:
        print(f"❌ Gagal ekspor data peserta: {response.text}")
        return False

def export_participants_csv(access_token: str, event_id: int = None) -> bool:
    """Ekspor data peserta ke CSV"""
    url = f"{BASE_URL}/api/v1/export/participants/csv"
    if event_id:
        url += f"?event_id={event_id}"
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        # Simpan file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if event_id:
            filename = f"data_peserta_event_{event_id}_{timestamp}.csv"
        else:
            filename = f"data_peserta_semua_{timestamp}.csv"
        
        with open(filename, "wb") as f:
            f.write(response.content)
        
        print(f"✅ Data peserta berhasil diekspor ke: {filename}")
        return True
    else:
        print(f"❌ Gagal ekspor data peserta: {response.text}")
        return False

def export_certificates_excel(access_token: str, event_id: int = None) -> bool:
    """Ekspor data sertifikat ke Excel"""
    url = f"{BASE_URL}/api/v1/export/certificates/excel"
    if event_id:
        url += f"?event_id={event_id}"
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        # Simpan file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if event_id:
            filename = f"data_sertifikat_event_{event_id}_{timestamp}.xlsx"
        else:
            filename = f"data_sertifikat_semua_{timestamp}.xlsx"
        
        with open(filename, "wb") as f:
            f.write(response.content)
        
        print(f"✅ Data sertifikat berhasil diekspor ke: {filename}")
        return True
    else:
        print(f"❌ Gagal ekspor data sertifikat: {response.text}")
        return False

def export_certificates_csv(access_token: str, event_id: int = None) -> bool:
    """Ekspor data sertifikat ke CSV"""
    url = f"{BASE_URL}/api/v1/export/certificates/csv"
    if event_id:
        url += f"?event_id={event_id}"
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        # Simpan file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if event_id:
            filename = f"data_sertifikat_event_{event_id}_{timestamp}.csv"
        else:
            filename = f"data_sertifikat_semua_{timestamp}.csv"
        
        with open(filename, "wb") as f:
            f.write(response.content)
        
        print(f"✅ Data sertifikat berhasil diekspor ke: {filename}")
        return True
    else:
        print(f"❌ Gagal ekspor data sertifikat: {response.text}")
        return False

def main():
    """Fungsi utama untuk demo ekspor data"""
    print("🚀 Demo Fitur Ekspor Data Event Organizer")
    print("=" * 50)
    
    try:
        # Login sebagai admin
        print("🔐 Login sebagai admin...")
        access_token = login_user(ADMIN_EMAIL, ADMIN_PASSWORD)
        print("✅ Login berhasil!")
        
        print("\n📊 Ekspor Data Statistik:")
        print("-" * 30)
        
        # Ekspor statistik Excel
        export_statistics_excel(access_token)
        
        # Ekspor statistik CSV
        export_statistics_csv(access_token)
        
        print("\n👥 Ekspor Data Peserta:")
        print("-" * 30)
        
        # Ekspor semua data peserta Excel
        export_participants_excel(access_token)
        
        # Ekspor data peserta untuk event tertentu (contoh: event_id=1)
        export_participants_excel(access_token, event_id=1)
        
        # Ekspor semua data peserta CSV
        export_participants_csv(access_token)
        
        print("\n🎫 Ekspor Data Sertifikat:")
        print("-" * 30)
        
        # Ekspor semua data sertifikat Excel
        export_certificates_excel(access_token)
        
        # Ekspor data sertifikat untuk event tertentu (contoh: event_id=1)
        export_certificates_excel(access_token, event_id=1)
        
        # Ekspor semua data sertifikat CSV
        export_certificates_csv(access_token)
        
        print("\n✅ Demo ekspor data selesai!")
        print("📁 File-file hasil ekspor tersimpan di direktori saat ini.")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\n💡 Pastikan:")
        print("1. Server berjalan di http://localhost:8000")
        print("2. Database sudah terisi dengan data")
        print("3. Dependencies pandas dan openpyxl sudah terinstall")

if __name__ == "__main__":
    main()
