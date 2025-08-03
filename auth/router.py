from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.user import UserLogin, Token
from app.models.user import User
from app.db import get_db
from app.auth.jwt_handler import create_access_token
import hashlib

router = APIRouter(prefix="/login", tags=["Auth"])

def verify_password(plain_pwd, hashed_pwd):
    return hashlib.sha256(plain_pwd.encode()).hexdigest() == hashed_pwd

@router.post("/", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token_data = {"sub": db_user.username, "role": db_user.role}
    token = create_access_token(token_data)
    return {"access_token": token, "token_type": "bearer"}
