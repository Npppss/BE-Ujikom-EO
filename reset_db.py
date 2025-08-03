from app.db.database import engine
from sqlalchemy import text

def reset_database():
    """Reset database completely"""
    try:
        with engine.connect() as conn:
            # Drop and recreate public schema
            conn.execute(text('DROP SCHEMA public CASCADE'))
            conn.execute(text('CREATE SCHEMA public'))
            conn.commit()
            print("Database schema reset successfully!")
    except Exception as e:
        print(f"Error resetting database: {e}")

if __name__ == "__main__":
    reset_database() 