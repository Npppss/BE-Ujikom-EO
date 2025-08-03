from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi import Depends
import os
from dotenv import load_dotenv

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:12345678@database-ujikom.cax0e00wk2uu.us-east-1.rds.amazonaws.com:5432/event_organizer")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()