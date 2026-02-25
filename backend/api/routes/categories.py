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


UNCATEGORIZED_ID = "uncategorized"


@router.get("", response_model=List[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    """Get all categories with metadata"""
    categories = db.query(Category).order_by(Category.display_order).all()

    # Transform categories to handle JSON description field
    result = [
        CategoryResponse(
            id=cat.id,
            title=cat.title,
            description=cat.description[0] if cat.description and len(cat.description) > 0 else "",
            icon_name=cat.icon_name,
            color=cat.color,
            display_order=cat.display_order
        )
        for cat in categories
    ]

    # Append a synthetic catch-all for promoted tips with no assigned category.
    # The frontend hides this card when the location has no uncategorized tips.
    result.append(CategoryResponse(
        id=UNCATEGORIZED_ID,
        title="Other",
        description="Tips that didn't fit a specific category",
        icon_name=None,  # resolves to HelpCircle in the frontend iconMapper
        color=None,
        display_order=9999
    ))

    return result
