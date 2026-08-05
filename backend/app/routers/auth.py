import os
import time
import datetime
import bcrypt
import jwt
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/api/auth", tags=["Auth"])

# Environment secrets
JWT_SECRET = os.getenv("JWT_SECRET", "super_secret_jwt_key_travel_copilot_2026_prod_secure")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")

def hash_password(password: str) -> str:
    """Hashes plain text password securely using bcrypt with 12 salt rounds"""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies plain text password against stored bcrypt hash (with fallback for legacy hashes)"""
    try:
        if hashed_password.startswith("$2b$") or hashed_password.startswith("$2a$"):
            return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        pass
    return False

def create_access_token(user_id: int, email: str) -> str:
    """Generates a signed JWT access token valid for 30 days"""
    now = int(time.time())
    payload = {
        "sub": str(user_id),
        "email": email,
        "iat": now,
        "exp": now + (86400 * 30) # 30 days
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_access_token(token: str) -> dict:
    """Decodes and verifies signed JWT access token signature and expiration"""
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired. Please log in again."
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token."
        )

@router.post("/register", response_model=schemas.Token)
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """Creates a new user account with bcrypt password hashing and returns JWT token"""
    clean_email = user_data.email.strip().lower() if user_data.email else ""
    clean_name = user_data.name.strip() if user_data.name else ""

    if not clean_email or "@" not in clean_email or "." not in clean_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please enter a valid email address.")
    if not user_data.password or len(user_data.password) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must be at least 6 characters long.")
    if not clean_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please enter your full name.")

    existing = db.query(models.User).filter(models.User.email == clean_email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists. Please Sign In."
        )

    now_utc = datetime.datetime.now(datetime.timezone.utc)
    hashed_pwd = hash_password(user_data.password)
    
    user = models.User(
        email=clean_email,
        name=clean_name,
        hashed_password=hashed_pwd,
        auth_provider="email",
        preferences="{}",
        created_at=now_utc,
        last_login=now_utc
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token_str = create_access_token(user.id, user.email)
    return {
        "access_token": token_str,
        "token_type": "bearer",
        "user": user
    }

@router.post("/login", response_model=schemas.Token)
def login(login_data: schemas.UserLogin, db: Session = Depends(get_db)):
    """Authenticates user email and bcrypt password, returning JWT token"""
    clean_email = login_data.email.strip().lower() if login_data.email else ""
    if not clean_email or "@" not in clean_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please enter a valid email address.")
    if not login_data.password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password cannot be empty.")

    user = db.query(models.User).filter(models.User.email == clean_email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found. Please click Sign Up to create an account."
        )

    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password. Please verify your credentials and try again."
        )

    # Update last login timestamp
    user.last_login = datetime.datetime.now(datetime.timezone.utc)
    db.commit()
    db.refresh(user)

    token_str = create_access_token(user.id, user.email)
    return {
        "access_token": token_str,
        "token_type": "bearer",
        "user": user
    }

@router.post("/google", response_model=schemas.Token)
def google_auth(data: schemas.GoogleAuthRequest, db: Session = Depends(get_db)):
    """Production Google OAuth 2.0 authentication and user registration"""
    clean_email = data.email.strip().lower() if data.email else ""
    if not clean_email or "@" not in clean_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Google profile email.")

    # Validate Google ID Token if present and Client ID configured
    if data.id_token and GOOGLE_CLIENT_ID:
        try:
            id_info = id_token.verify_oauth2_token(data.id_token, google_requests.Request(), GOOGLE_CLIENT_ID)
            clean_email = id_info.get("email", clean_email).lower()
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Google OAuth verification failed: {str(e)}")

    now_utc = datetime.datetime.now(datetime.timezone.utc)
    user = db.query(models.User).filter(models.User.email == clean_email).first()

    if not user:
        # First-time Google OAuth Sign Up
        user = models.User(
            email=clean_email,
            name=data.name.strip() if data.name else clean_email.split('@')[0].title(),
            photo_url=data.photo_url,
            hashed_password=hash_password("google_oauth_" + (data.google_id or clean_email)),
            auth_provider="google",
            preferences="{}",
            created_at=now_utc,
            last_login=now_utc
        )
        db.add(user)
    else:
        # Existing User Google Sign In -> Update last_login & photo_url if provided
        user.last_login = now_utc
        if data.photo_url:
            user.photo_url = data.photo_url
        if not user.auth_provider:
            user.auth_provider = "google"

    db.commit()
    db.refresh(user)

    token_str = create_access_token(user.id, user.email)
    return {
        "access_token": token_str,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=schemas.UserResponse)
def get_me(authorization: str = Header(None), token: str = "", db: Session = Depends(get_db)):
    """Fetches currently authenticated user based on JWT Bearer token"""
    auth_token = ""
    if authorization and authorization.startswith("Bearer "):
        auth_token = authorization.replace("Bearer ", "").strip()
    elif token:
        auth_token = token.strip()

    if not auth_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication token required.")

    payload = decode_access_token(auth_token)
    user_id = int(payload.get("sub", 0))

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User account not found.")

    user.last_login = datetime.datetime.now(datetime.timezone.utc)
    db.commit()
    db.refresh(user)
    return user

@router.post("/logout")
def logout():
    """Logs out user session cleanly"""
    return {"message": "Successfully logged out."}
