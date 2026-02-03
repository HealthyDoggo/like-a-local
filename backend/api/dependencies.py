"""Shared API dependencies"""
from typing import Generator, Optional
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from backend.database.connection import get_db
from backend.database.models import User
from backend.services.auth import decode_token


def get_database() -> Generator[Session, None, None]:
    """Dependency for database session"""
    yield from get_db()


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_database)
) -> User:
    """
    Validate JWT and return current user.
    Raises 401 if token is invalid or user not found.
    """
    token = credentials.credentials

    # Decode and verify token
    payload = decode_token(token)
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    # Get user from database
    user = db.query(User).filter(
        User.id == int(user_id),
        User.is_active == True
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_database)
) -> Optional[User]:
    """
    Get user if authenticated, None otherwise.
    Used for endpoints where authentication is optional.
    """
    if not credentials:
        return None

    try:
        # Reuse the get_current_user logic
        token = credentials.credentials
        payload = decode_token(token)
        user_id = payload.get("sub")

        if not user_id:
            return None

        user = db.query(User).filter(
            User.id == int(user_id),
            User.is_active == True
        ).first()

        return user
    except:
        # If anything goes wrong, just return None (optional auth)
        return None

