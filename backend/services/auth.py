"""Authentication service for JWT, passwords, and OAuth verification"""
from datetime import datetime, timedelta
from typing import Optional
import secrets

from jose import JWTError, jwt
from passlib.context import CryptContext
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from backend.config import settings
from backend.database.models import User, RefreshToken


# Password hashing context (bcrypt with cost factor 12)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Password hashing
def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password.encode("utf-8")[:72])


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password.encode("utf-8")[:72], hashed_password)


# JWT token creation
def create_access_token(user_id: int, email: str) -> str:
    """Create a JWT access token (15 minutes expiry)"""
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": expire,
        "type": "access"
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(user_id: int, db: Session) -> str:
    """Create a refresh token and store it in the database (7 days expiry)"""
    # Generate a secure random token
    token = secrets.token_urlsafe(64)
    expires_at = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)

    # Store in database
    db_token = RefreshToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )
    db.add(db_token)
    db.commit()

    return token


def decode_token(token: str) -> dict:
    """Decode and verify a JWT token"""
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Google OAuth verification
def verify_google_token(id_token: str) -> dict:
    """
    Verify Google ID token server-side.
    Returns user info: {'sub': google_id, 'email': email, 'name': name, 'picture': url}
    """
    try:
        # Verify the token with Google
        idinfo = google_id_token.verify_oauth2_token(
            id_token,
            google_requests.Request(),
            settings.google_client_id
        )

        # Verify the issuer
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        # Return user info
        return {
            'google_id': idinfo['sub'],
            'email': idinfo['email'],
            'name': idinfo.get('name'),
            'picture': idinfo.get('picture'),
            'email_verified': idinfo.get('email_verified', False)
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Google token: {str(e)}"
        )


# User creation and authentication
def get_or_create_google_user(
    google_id: str,
    email: str,
    name: Optional[str],
    picture: Optional[str],
    db: Session
) -> User:
    """Get existing Google user or create new one"""
    # Check if user exists by google_id
    user = db.query(User).filter(User.google_id == google_id).first()

    if user:
        # Update last login and profile data
        user.last_login = datetime.utcnow()
        if name:
            user.full_name = name
        if picture:
            user.profile_picture_url = picture
        db.commit()
        db.refresh(user)
        return user

    # Check if user exists by email (might have signed up with email first)
    user = db.query(User).filter(User.email == email).first()
    if user:
        # Link Google account to existing user
        user.google_id = google_id
        user.auth_provider = 'google'
        user.email_verified = True
        user.last_login = datetime.utcnow()
        if name:
            user.full_name = name
        if picture:
            user.profile_picture_url = picture
        db.commit()
        db.refresh(user)
        return user

    # Create new user
    user = User(
        email=email,
        google_id=google_id,
        auth_provider='google',
        email_verified=True,
        full_name=name,
        profile_picture_url=picture,
        last_login=datetime.utcnow()
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_email_user(
    email: str,
    password: str,
    full_name: str,
    preferred_language: str,
    db: Session
) -> User:
    """Create a new user with email/password authentication"""
    # Check if user already exists
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user
    user = User(
        email=email,
        hashed_password=hash_password(password),
        auth_provider='email',
        full_name=full_name,
        preferred_language=preferred_language,
        email_verified=False,  # Can implement email verification later
        last_login=datetime.utcnow()
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_email_user(email: str, password: str, db: Session) -> Optional[User]:
    """Authenticate a user with email and password"""
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return None

    if not user.hashed_password:
        # User signed up with OAuth, doesn't have a password
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This account uses OAuth authentication. Please sign in with Google."
        )

    if not verify_password(password, user.hashed_password):
        return None

    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    db.refresh(user)

    return user


def get_refresh_token_from_db(token: str, db: Session) -> Optional[RefreshToken]:
    """Get a refresh token from the database if valid"""
    db_token = db.query(RefreshToken).filter(
        RefreshToken.token == token,
        RefreshToken.revoked == False
    ).first()

    if not db_token:
        return None

    # Check if expired
    if db_token.expires_at < datetime.utcnow():
        return None

    return db_token


def revoke_refresh_token(token: str, db: Session) -> bool:
    """Revoke a refresh token"""
    db_token = db.query(RefreshToken).filter(RefreshToken.token == token).first()
    if db_token:
        db_token.revoked = True
        db.commit()
        return True
    return False
