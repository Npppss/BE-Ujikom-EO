#!/usr/bin/env python3

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.security import get_password_hash
from datetime import datetime

# Use SQLite directly
DATABASE_URL = "sqlite:///./event_organizer.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables_and_admin():
    """Create basic tables and admin user"""
    
    # Create tables
    with engine.connect() as conn:
        # Create roles table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(50) UNIQUE NOT NULL,
                description TEXT,
                permissions TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Create users table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email VARCHAR(255) UNIQUE NOT NULL,
                hashed_password VARCHAR(255) NOT NULL,
                full_name VARCHAR(255),
                is_active BOOLEAN DEFAULT TRUE,
                is_verified BOOLEAN DEFAULT TRUE,
                email_verification_token VARCHAR(255),
                email_verification_expires TIMESTAMP,
                role_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (role_id) REFERENCES roles (id)
            )
        """))
        
        # Insert roles
        conn.execute(text("""
            INSERT OR IGNORE INTO roles (name, description, permissions) VALUES 
            ('admin', 'Administrator with full access', '["all"]'),
            ('organizer', 'Event organizer', '["event:manage"]'),
            ('user', 'Regular user', '["event:view"]')
        """))
        
        # Insert admin user
        admin_password = get_password_hash("admin123")
        conn.execute(text("""
            INSERT OR IGNORE INTO users (email, hashed_password, full_name, is_active, is_verified, role_id) 
            VALUES ('admin@epicvibe.com', :password, 'Admin User', 1, 1, 1)
        """), {"password": admin_password})
        
        # Insert demo users
        user_password = get_password_hash("user123")
        organizer_password = get_password_hash("organizer123")
        
        conn.execute(text("""
            INSERT OR IGNORE INTO users (email, hashed_password, full_name, is_active, is_verified, role_id) 
            VALUES 
            ('user@epicvibe.com', :user_password, 'Demo User', 1, 1, 3),
            ('organizer@epicvibe.com', :organizer_password, 'Demo Organizer', 1, 1, 2)
        """), {"user_password": user_password, "organizer_password": organizer_password})
        
        conn.commit()
        
    print("✅ Database and admin user created successfully!")
    print("📧 Admin: admin@epicvibe.com / admin123")
    print("👤 User: user@epicvibe.com / user123")
    print("🎪 Organizer: organizer@epicvibe.com / organizer123")

if __name__ == "__main__":
    create_tables_and_admin()