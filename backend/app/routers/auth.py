import hashlib
import json
import base64
import time
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/api/auth", tags=["Auth"])

def hash_password(password: str) -> str:
    return hashlib.sha256((password + "salt_2026_travel_copilot").encode('utf-8')).hexdigest()

def create_token(user_id: int, email: str) -> str:
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": int(time.time()) + 86400 * 30
    }
    raw = json.dumps(payload).encode('utf-8')
    return base64.b64encode(raw).decode('utf-8')

def decode_token(token: str) -> dict:
    try:
        raw = base64.b64decode(token.encode('utf-8')).decode('utf-8')
        return json.loads(raw)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

@router.post("/register", response_model=schemas.Token)
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    if not user_data.email or "@" not in user_data.email:
        raise HTTPException(status_code=400, detail="Please enter a valid email address.")
    if not user_data.password or len(user_data.password) < 4:
        raise HTTPException(status_code=400, detail="Password must be at least 4 characters long.")
    if not user_data.name or not user_data.name.strip():
        raise HTTPException(status_code=400, detail="Please enter your full name.")

    existing = db.query(models.User).filter(models.User.email == user_data.email.strip().lower()).first()
    if existing:
        raise HTTPException(status_code=400, detail="An account with this email already exists. Please Sign In.")
    
    hashed = hash_password(user_data.password)
    user = models.User(
        email=user_data.email.strip().lower(),
        name=user_data.name.strip(),
        hashed_password=hashed,
        preferences="{}"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token_str = create_token(user.id, user.email)
    return {
        "access_token": token_str,
        "token_type": "bearer",
        "user": user
    }

@router.post("/login", response_model=schemas.Token)
def login(login_data: schemas.UserLogin, db: Session = Depends(get_db)):
    clean_email = login_data.email.strip().lower() if login_data.email else ""
    if not clean_email or "@" not in clean_email:
        raise HTTPException(status_code=400, detail="Please enter a valid email address.")
    if not login_data.password:
        raise HTTPException(status_code=400, detail="Password cannot be empty.")

    hashed = hash_password(login_data.password)
    user = db.query(models.User).filter(
        models.User.email == clean_email,
        models.User.hashed_password == hashed
    ).first()

    if not user:
        email_exists = db.query(models.User).filter(models.User.email == clean_email).first()
        if email_exists:
            raise HTTPException(status_code=401, detail="Incorrect password. Please try again.")
        else:
            raise HTTPException(status_code=404, detail="Account not found. Please click Sign Up to create an account.")

    token_str = create_token(user.id, user.email)
    return {
        "access_token": token_str,
        "token_type": "bearer",
        "user": user
    }

@router.post("/google", response_model=schemas.Token)
def google_auth(data: schemas.GoogleAuthRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email).first()
    if not user:
        user = models.User(
            email=data.email,
            name=data.name or data.email.split('@')[0].title(),
            hashed_password=hash_password("google_oauth_" + (data.google_id or data.email)),
            preferences="{}"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    token_str = create_token(user.id, user.email)
    return {
        "access_token": token_str,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=schemas.UserResponse)
def get_me(token: str = "", user_id: int = 1, db: Session = Depends(get_db)):
    if token:
        payload = decode_token(token)
        uid = int(payload.get("sub", user_id))
    else:
        uid = user_id
        
    user = db.query(models.User).filter(models.User.id == uid).first()
    if not user:
        user = models.User(
            email="traveler@example.com",
            name="Traveler",
            hashed_password=hash_password("password123"),
            preferences="{}"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user
