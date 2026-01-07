"""Shared API dependencies"""
from typing import Generator
from sqlalchemy.orm import Session
from backend.database.connection import get_db


def get_database() -> Generator[Session, None, None]:
    """Dependency for database session"""
    yield from get_db()

