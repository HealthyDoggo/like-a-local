"""Authentication endpoints"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from backend.api.dependencies import get_database
from backend.database.models import User
from backend.api.dependencies import get_current_user
from backend.services.auth import (
    create_access_token,
    create_refresh_token,
    create_email_user,
    authenticate_email_user,
    verify_google_token,
    get_or_create_google_user,
    decode_token,
    get_refresh_token_from_db,
    revoke_refresh_token
)


router = APIRouter(prefix="/api/auth", tags=["authentication"])


# Pydantic models
class EmailSignUpRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    full_name: str = Field(..., min_length=1)
    preferred_language: Optional[str] = "en"


class EmailSignInRequest(BaseModel):
    email: EmailStr
    password: str


class GoogleAuthRequest(BaseModel):
    id_token: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    profile_picture_url: Optional[str]
    preferred_language: str
    auth_provider: str
    email_verified: bool

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


# Helper function to create token response
def create_token_response(user: User, db: Session) -> TokenResponse:
    """Create a token response with access and refresh tokens"""
    access_token = create_access_token(user.id, user.email)
    refresh_token = create_refresh_token(user.id, db)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user)
    )


# Endpoints
@router.post("/signup/email", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def sign_up_with_email(
    request: EmailSignUpRequest,
    db: Session = Depends(get_database)
):
    """Register a new user with email and password"""
    user = create_email_user(
        email=request.email,
        password=request.password,
        full_name=request.full_name,
        preferred_language=request.preferred_language or "en",
        db=db
    )

    return create_token_response(user, db)


@router.post("/signin/email", response_model=TokenResponse)
def sign_in_with_email(
    request: EmailSignInRequest,
    db: Session = Depends(get_database)
):
    """Sign in with email and password"""
    user = authenticate_email_user(request.email, request.password, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )

    return create_token_response(user, db)


@router.post("/google", response_model=TokenResponse)
def sign_in_with_google(
    request: GoogleAuthRequest,
    db: Session = Depends(get_database)
):
    """Sign in or sign up with Google OAuth"""
    # Verify the Google ID token
    google_info = verify_google_token(request.id_token)

    # Get or create user
    user = get_or_create_google_user(
        google_id=google_info['google_id'],
        email=google_info['email'],
        name=google_info.get('name'),
        picture=google_info.get('picture'),
        db=db
    )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )

    return create_token_response(user, db)


@router.post("/refresh", response_model=TokenResponse)
def refresh_access_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_database)
):
    """Refresh an access token using a refresh token"""
    # Validate refresh token
    db_token = get_refresh_token_from_db(request.refresh_token, db)

    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    # Get user
    user = db.query(User).filter(User.id == db_token.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    # Create new tokens
    return create_token_response(user, db)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    request: RefreshTokenRequest,
    db: Session = Depends(get_database)
):
    """Logout by revoking the refresh token"""
    revoke_refresh_token(request.refresh_token, db)
    return None


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current authenticated user information"""
    return UserResponse.model_validate(current_user)
