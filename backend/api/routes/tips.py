"""Tip API endpoints"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from pydantic import BaseModel, Field
from datetime import datetime

from backend.database.models import Tip, Location, Embedding, TipTranslation, User
from backend.api.dependencies import get_database, get_current_user_optional, get_current_user

router = APIRouter(prefix="/api/tips", tags=["tips"])


class TipCreate(BaseModel):
    """Tip creation request model"""
    tip_text: str = Field(..., min_length=1, max_length=5000)
    location_name: Optional[str] = None
    location_country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    user_id: Optional[int] = None
    category_id: Optional[str] = None


class TipResponse(BaseModel):
    """Tip response model"""
    id: int
    tip_text: str
    original_language: Optional[str]
    translated_text: Optional[str]
    location_id: Optional[int]
    location_name: Optional[str] = None
    location_country: Optional[str] = None
    user_id: Optional[int]
    submitted_at: datetime
    processed_at: Optional[datetime]
    status: str
    category_id: Optional[str] = None
    category_confidence: Optional[float] = None

    model_config = {"from_attributes": True}


@router.post("", response_model=TipResponse, status_code=201)
async def create_tip(
    tip: TipCreate,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_database)
):
    """Submit a new tip (authentication optional)"""
    # Get or create location
    location_id = None
    if tip.location_name and tip.location_country:
        location = db.query(Location).filter(
            Location.name == tip.location_name,
            Location.country == tip.location_country
        ).first()

        if not location:
            location = Location(
                name=tip.location_name,
                country=tip.location_country,
                latitude=tip.latitude,
                longitude=tip.longitude
            )
            db.add(location)
            db.commit()
            db.refresh(location)

        location_id = location.id

    # Create tip with user_id from authenticated user if available
    db_tip = Tip(
        tip_text=tip.tip_text,
        location_id=location_id,
        user_id=current_user.id if current_user else None,
        status="pending",
        category_id=tip.category_id,
        category_manual=bool(tip.category_id)
    )
    db.add(db_tip)
    db.commit()
    db.refresh(db_tip)
    
    # Add location info to response
    response = TipResponse.model_validate(db_tip)
    if location_id:
        location = db.query(Location).filter(Location.id == location_id).first()
        if location:
            response.location_name = location.name
            response.location_country = location.country
    
    return response


@router.get("", response_model=List[TipResponse])
def get_tips(
    location_id: Optional[int] = Query(None, description="Filter by location ID"),
    category_id: Optional[str] = Query(None, description="Filter by category ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    language: str = Query("en", description="Preferred language code (e.g., en, es, fr)"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_database)
):
    """
    Query tips with language preference.

    Returns tips in the requested language with fallback chain:
    preferred language → English → original language
    """
    # Query tips with LEFT JOIN to get translation in preferred language
    tips_query = (
        db.query(Tip, TipTranslation.translated_text.label('preferred_translation'))
        .outerjoin(
            TipTranslation,
            and_(
                TipTranslation.tip_id == Tip.id,
                TipTranslation.language_code == language
            )
        )
    )

    # Apply filters
    if location_id:
        tips_query = tips_query.filter(Tip.location_id == location_id)

    if category_id:
        tips_query = tips_query.filter(Tip.category_id == category_id)

    if status:
        tips_query = tips_query.filter(Tip.status == status)

    # Execute query
    results_data = tips_query.order_by(Tip.submitted_at.desc()).limit(limit).offset(offset).all()

    # Build response with fallback chain
    results = []
    for tip, preferred_translation in results_data:
        # Fallback chain: preferred language → English → original
        tip_text = (
            preferred_translation or
            tip.translated_text or
            tip.tip_text
        )

        # Create response with translated text
        response = TipResponse.model_validate(tip)
        response.tip_text = tip_text

        # Add location info
        if tip.location_id:
            location = db.query(Location).filter(Location.id == tip.location_id).first()
            if location:
                response.location_name = location.name
                response.location_country = location.country

        results.append(response)

    return results


@router.get("/me", response_model=List[TipResponse])
async def get_my_tips(
    language: str = Query("en", description="Preferred language code (e.g., en, es, fr)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    """Get all tips submitted by the authenticated user, in the requested language."""
    tips_query = (
        db.query(Tip, TipTranslation.translated_text.label("preferred_translation"))
        .outerjoin(
            TipTranslation,
            and_(
                TipTranslation.tip_id == Tip.id,
                TipTranslation.language_code == language
            )
        )
        .filter(Tip.user_id == current_user.id)
        .order_by(Tip.submitted_at.desc())
    )

    results = []
    for tip, preferred_translation in tips_query.all():
        tip_text = preferred_translation or tip.translated_text or tip.tip_text
        response = TipResponse.model_validate(tip)
        response.tip_text = tip_text
        if tip.location_id:
            location = db.query(Location).filter(Location.id == tip.location_id).first()
            if location:
                response.location_name = location.name
                response.location_country = location.country
        results.append(response)

    return results


@router.get("/{tip_id}", response_model=TipResponse)
def get_tip(
    tip_id: int,
    db: Session = Depends(get_database)
):
    """Get a specific tip by ID"""
    tip = db.query(Tip).filter(Tip.id == tip_id).first()
    if not tip:
        raise HTTPException(status_code=404, detail="Tip not found")

    response = TipResponse.model_validate(tip)
    if tip.location_id:
        location = db.query(Location).filter(Location.id == tip.location_id).first()
        if location:
            response.location_name = location.name
            response.location_country = location.country

    return response

