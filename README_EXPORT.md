# Event Organizer - Export Data System

Sistem ekspor data lengkap untuk Event Organizer yang memungkinkan admin dan organizer untuk mengekspor data statistik dan data peserta ke format Excel (.xlsx) dan CSV.

## Fitur yang Tersedia

### 1. Ekspor Data Statistik
- **Statistik Bulanan**: Jumlah kegiatan terlaksana dan peserta hadir per bulan (Januari-Desember)
- **Top 10 Kegiatan**: Sepuluh kegiatan dengan jumlah peserta terbanyak
- **Format Excel**: File .xlsx dengan multiple sheet
- **Format CSV**: File .csv dengan data terstruktur

### 2. Ekspor Data Peserta
- **Data Lengkap**: Nama, email, kegiatan, status registrasi, kehadiran
- **Filter per Event**: Dapat mengekspor data peserta untuk event tertentu
- **Status Kehadiran**: Informasi check-in dan check-out
- **Data Pembayaran**: Informasi tipe tiket dan harga

### 3. Ekspor Data Sertifikat
- **Data Sertifikat**: ID sertifikat, nama peserta, status terbit
- **Status Verifikasi**: Informasi verifikasi sertifikat
- **Filter per Event**: Dapat mengekspor data sertifikat untuk event tertentu

## Setup dan Instalasi

### 1. Install Dependencies
```bash
pip install pandas openpyxl
```

### 2. Update Requirements
Pastikan `requirements.txt` sudah berisi:
```
pandas
openpyxl
```

### 3. Restart Aplikasi
```bash
uvicorn app.main:app --reload
```

## API Endpoints

### Ekspor Statistik

#### Export Statistics to Excel
```http
GET /api/v1/export/statistics/excel
Authorization: Bearer <access_token>
```

**Response**: File Excel (.xlsx) dengan 2 sheet:
- **Sheet 1**: Statistik Bulanan
- **Sheet 2**: Top 10 Kegiatan

#### Export Statistics to CSV
```http
GET /api/v1/export/statistics/csv
Authorization: Bearer <access_token>
```

**Response**: File CSV dengan format:
```
STATISTIK KEGIATAN PER BULAN
==================================================
Bulan,Jumlah Kegiatan Terlaksana,Jumlah Peserta Hadir
Januari 2024,5,150
Februari 2024,3,89
...

10 KEGIATAN DENGAN PESERTA TERBANYAK
==================================================
Peringkat,Judul Kegiatan,Kategori,Tanggal,Jumlah Peserta,Lokasi
1,Workshop Python,Technology,15/01/2024,45,Jakarta
2,Seminar Bisnis,Business,20/01/2024,38,Bandung
...
```

### Ekspor Data Peserta

#### Export All Participants to Excel
```http
GET /api/v1/export/participants/excel
Authorization: Bearer <access_token>
```

#### Export Participants for Specific Event to Excel
```http
GET /api/v1/export/participants/excel?event_id=1
Authorization: Bearer <access_token>
```

**Response**: File Excel (.xlsx) dengan kolom:
- Nama Lengkap
- Email
- Judul Kegiatan
- Tanggal Kegiatan
- Lokasi
- Tanggal Registrasi
- Status Registrasi
- Tipe Tiket
- Harga Dibayar
- Waktu Check-in
- Waktu Check-out
- Status Check-in
- Status Check-out

#### Export All Participants to CSV
```http
GET /api/v1/export/participants/csv
Authorization: Bearer <access_token>
```

#### Export Participants for Specific Event to CSV
```http
GET /api/v1/export/participants/csv?event_id=1
Authorization: Bearer <access_token>
```

### Ekspor Data Sertifikat

#### Export All Certificates to Excel
```http
GET /api/v1/export/certificates/excel
Authorization: Bearer <access_token>
```

#### Export Certificates for Specific Event to Excel
```http
GET /api/v1/export/certificates/excel?event_id=1
Authorization: Bearer <access_token>
```

**Response**: File Excel (.xlsx) dengan kolom:
- ID Sertifikat
- Nama Peserta
- Email
- Nama Kegiatan
- Tanggal Kegiatan
- Tipe Sertifikat
- Status Terbit
- Tanggal Terbit
- Status Valid
- Status Verifikasi
- Tanggal Verifikasi

#### Export All Certificates to CSV
```http
GET /api/v1/export/certificates/csv
Authorization: Bearer <access_token>
```

#### Export Certificates for Specific Event to CSV
```http
GET /api/v1/export/certificates/csv?event_id=1
Authorization: Bearer <access_token>
```

## Permission Requirements

### Statistik dan Data Peserta
- **Permission**: `event:read`
- **Access**: Admin dapat melihat semua data, Organizer hanya data event mereka

### Data Sertifikat
- **Permission**: `certificate:read`
- **Access**: Admin dapat melihat semua data, Organizer hanya data event mereka

## Format Data

### Statistik Bulanan
Data yang diekspor mencakup:
- **Bulan**: Nama bulan dan tahun (Januari 2024, Februari 2024, dst)
- **Jumlah Kegiatan Terlaksana**: Event dengan status COMPLETED
- **Jumlah Peserta Hadir**: Peserta yang melakukan check-in (check_in_qr_scanned = true)

### Top 10 Kegiatan
Data yang diekspor mencakup:
- **Peringkat**: Urutan berdasarkan jumlah peserta
- **Judul Kegiatan**: Nama event
- **Kategori**: Kategori event (Business, Technology, dll)
- **Tanggal**: Tanggal pelaksanaan event
- **Jumlah Peserta**: Jumlah peserta yang hadir
- **Lokasi**: Lokasi event

### Data Peserta
Data yang diekspor mencakup:
- **Informasi Pribadi**: Nama lengkap, email
- **Informasi Event**: Judul, tanggal, lokasi
- **Informasi Registrasi**: Tanggal registrasi, status, tipe tiket, harga
- **Informasi Kehadiran**: Waktu check-in/out, status kehadiran

### Data Sertifikat
Data yang diekspor mencakup:
- **Informasi Sertifikat**: ID, tipe, status terbit
- **Informasi Peserta**: Nama, email
- **Informasi Event**: Nama, tanggal
- **Informasi Verifikasi**: Status valid, status verifikasi, tanggal verifikasi

## Contoh Penggunaan

### Frontend Integration (JavaScript)
```javascript
// Export statistics to Excel
const exportStatistics = async () => {
  try {
    const response = await fetch('/api/v1/export/statistics/excel', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    });
    
    if (response.ok) {
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'statistik_kegiatan.xlsx';
      a.click();
      window.URL.revokeObjectURL(url);
    }
  } catch (error) {
    console.error('Export failed:', error);
  }
};

// Export participants for specific event
const exportEventParticipants = async (eventId) => {
  try {
    const response = await fetch(`/api/v1/export/participants/excel?event_id=${eventId}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    });
    
    if (response.ok) {
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `data_peserta_event_${eventId}.xlsx`;
      a.click();
      window.URL.revokeObjectURL(url);
    }
  } catch (error) {
    console.error('Export failed:', error);
  }
};
```

### React Component Example
```jsx
import React from 'react';

const ExportButtons = ({ eventId }) => {
  const handleExportStatistics = async () => {
    // Implementation for statistics export
  };

  const handleExportParticipants = async () => {
    // Implementation for participants export
  };

  const handleExportCertificates = async () => {
    // Implementation for certificates export
  };

  return (
    <div className="export-buttons">
      <button onClick={handleExportStatistics}>
        Export Statistik (Excel)
      </button>
      <button onClick={handleExportParticipants}>
        Export Data Peserta (Excel)
      </button>
      <button onClick={handleExportCertificates}>
        Export Data Sertifikat (Excel)
      </button>
    </div>
  );
};
```

## Error Handling

### Common Error Responses

#### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

#### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

#### 500 Internal Server Error
```json
{
  "detail": "Failed to export data: [error message]"
}
```

## Performance Considerations

### 1. Large Data Sets
- Untuk data besar, pertimbangkan pagination atau filtering
- Gunakan parameter `event_id` untuk membatasi data yang diekspor

### 2. Memory Usage
- Export service menggunakan memory untuk generate file
- Untuk data sangat besar, pertimbangkan background job

### 3. File Size
- Excel files bisa besar untuk data banyak
- CSV lebih efisien untuk data besar

## Security Features

### 1. Permission-based Access
- Hanya user dengan permission yang tepat yang bisa ekspor
- Admin dapat ekspor semua data
- Organizer hanya dapat ekspor data event mereka

### 2. Data Filtering
- Data difilter berdasarkan role user
- Tidak ada data yang tidak seharusnya diakses

### 3. File Naming
- File menggunakan timestamp untuk menghindari konflik
- Nama file tidak mengandung informasi sensitif

## Troubleshooting

### Common Issues

1. **File Not Downloading**
   - Periksa permission user
   - Pastikan token masih valid
   - Check browser download settings

2. **Empty Data**
   - Periksa apakah ada data di database
   - Pastikan filter tidak terlalu ketat
   - Check event status (COMPLETED untuk statistik)

3. **Large File Size**
   - Gunakan filter event_id untuk membatasi data
   - Pertimbangkan menggunakan CSV format
   - Implement background job untuk data besar

4. **Permission Denied**
   - Periksa role dan permission user
   - Pastikan endpoint memerlukan permission yang tepat

## Production Considerations

### 1. Performance
- Monitor memory usage saat export
- Implement caching untuk data yang sering diekspor
- Consider background jobs untuk export besar

### 2. Security
- Validate all input parameters
- Implement rate limiting untuk export endpoints
- Log export activities untuk audit

### 3. Monitoring
- Track export usage patterns
- Monitor file sizes and download times
- Alert on failed exports

---

**Export System Ready for Production Use**
