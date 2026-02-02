"""Category API routes"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.database.models import Category
from pydantic import BaseModel

router = APIRouter(prefix="/api/categories", tags=["categories"])


class CategoryResponse(BaseModel):
    """Category response model"""
    id: str
    title: str
    description: str
    icon_name: str | None
    color: str | None
    display_order: int | None

    class Config:
        from_attributes = True


@router.get("", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    """Get all categories with metadata"""
    categories = db.query(Category).order_by(Category.display_order).all()
    return categories
