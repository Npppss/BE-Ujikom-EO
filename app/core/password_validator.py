import re
from typing import Tuple, List

class PasswordValidator:
    """
    Password validator dengan regex untuk memastikan password strength sesuai requirement:
    - Minimal 8 karakter
    - Mengandung angka
    - Mengandung huruf besar
    - Mengandung huruf kecil
    - Mengandung karakter spesial
    """
    
    def __init__(self):
        # Regex patterns untuk validasi password
        self.min_length = 8
        self.patterns = {
            'length': r'.{8,}',  # Minimal 8 karakter
            'uppercase': r'[A-Z]',  # Huruf besar
            'lowercase': r'[a-z]',  # Huruf kecil
            'digit': r'\d',  # Angka
            'special': r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]'  # Karakter spesial
        }
        
        # Pesan error untuk setiap validasi
        self.error_messages = {
            'length': f'Password harus minimal {self.min_length} karakter',
            'uppercase': 'Password harus mengandung minimal 1 huruf besar',
            'lowercase': 'Password harus mengandung minimal 1 huruf kecil',
            'digit': 'Password harus mengandung minimal 1 angka',
            'special': 'Password harus mengandung minimal 1 karakter spesial (!@#$%^&*()_+-=[]{}|;:,.<>?)'
        }
    
    def validate_password(self, password: str) -> Tuple[bool, List[str]]:
        """
        Validasi password strength
        
        Args:
            password (str): Password yang akan divalidasi
            
        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_errors)
        """
        errors = []
        
        # Validasi panjang minimal
        if not re.search(self.patterns['length'], password):
            errors.append(self.error_messages['length'])
        
        # Validasi huruf besar
        if not re.search(self.patterns['uppercase'], password):
            errors.append(self.error_messages['uppercase'])
        
        # Validasi huruf kecil
        if not re.search(self.patterns['lowercase'], password):
            errors.append(self.error_messages['lowercase'])
        
        # Validasi angka
        if not re.search(self.patterns['digit'], password):
            errors.append(self.error_messages['digit'])
        
        # Validasi karakter spesial
        if not re.search(self.patterns['special'], password):
            errors.append(self.error_messages['special'])
        
        return len(errors) == 0, errors
    
    def get_password_strength(self, password: str) -> str:
        """
        Menentukan strength password berdasarkan jumlah kriteria yang terpenuhi
        
        Args:
            password (str): Password yang akan dianalisis
            
        Returns:
            str: 'weak', 'medium', 'strong', atau 'very_strong'
        """
        criteria_met = 0
        
        # Hitung berapa kriteria yang terpenuhi
        if re.search(self.patterns['length'], password):
            criteria_met += 1
        if re.search(self.patterns['uppercase'], password):
            criteria_met += 1
        if re.search(self.patterns['lowercase'], password):
            criteria_met += 1
        if re.search(self.patterns['digit'], password):
            criteria_met += 1
        if re.search(self.patterns['special'], password):
            criteria_met += 1
        
        # Tentukan strength berdasarkan jumlah kriteria
        if criteria_met <= 2:
            return 'weak'
        elif criteria_met == 3:
            return 'medium'
        elif criteria_met == 4:
            return 'strong'
        else:
            return 'very_strong'
    
    def get_password_requirements(self) -> dict:
        """
        Mengembalikan daftar requirement password untuk ditampilkan ke user
        
        Returns:
            dict: Dictionary berisi requirement password
        """
        return {
            'min_length': self.min_length,
            'requirements': [
                f'Minimal {self.min_length} karakter',
                'Minimal 1 huruf besar (A-Z)',
                'Minimal 1 huruf kecil (a-z)',
                'Minimal 1 angka (0-9)',
                'Minimal 1 karakter spesial (!@#$%^&*()_+-=[]{}|;:,.<>?)'
            ],
            'example': 'Password123#'
        }
    
    def is_common_password(self, password: str) -> bool:
        """
        Cek apakah password termasuk password umum yang mudah ditebak
        
        Args:
            password (str): Password yang akan dicek
            
        Returns:
            bool: True jika password umum, False jika tidak
        """
        common_passwords = [
            'password', '123456', '123456789', 'qwerty', 'abc123',
            'password123', 'admin', 'admin123', 'letmein', 'welcome',
            'monkey', 'dragon', 'master', 'football', 'basketball',
            'sunshine', 'princess', 'superman', 'batman', 'spiderman',
            'hello', 'world', 'love', 'hate', 'fuck', 'shit', 'bitch',
            'test', 'testing', 'guest', 'user', 'demo', 'sample',
            'default', 'changeme', 'newpass', 'oldpass', 'mypass',
            'secret', 'private', 'public', 'temp', 'temporary'
        ]
        
        return password.lower() in common_passwords

# Instance global untuk digunakan di seluruh aplikasi
password_validator = PasswordValidator()
