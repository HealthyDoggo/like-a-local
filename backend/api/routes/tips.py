"""Tip API endpoints"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from datetime import datetime

from backend.database.models import Tip, Location, Embedding
from backend.api.dependencies import get_database

router = APIRouter(prefix="/api/tips", tags=["tips"])


class TipCreate(BaseModel):
    """Tip creation request model"""
    tip_text: str = Field(..., min_length=1, max_length=5000)
    location_name: Optional[str] = None
    location_country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    user_id: Optional[int] = None


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
    
    model_config = {"from_attributes": True}


@router.post("", response_model=TipResponse, status_code=201)
def create_tip(
    tip: TipCreate,
    db: Session = Depends(get_database)
):
    """Submit a new tip"""
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
    
    # Create tip
    db_tip = Tip(
        tip_text=tip.tip_text,
        location_id=location_id,
        user_id=tip.user_id,
        status="pending"
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
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_database)
):
    """Query processed tips with optional filters"""
    query = db.query(Tip)
    
    if location_id:
        query = query.filter(Tip.location_id == location_id)
    
    if status:
        query = query.filter(Tip.status == status)
    
    tips = query.order_by(Tip.submitted_at.desc()).limit(limit).offset(offset).all()
    
    # Add location info to responses
    results = []
    for tip in tips:
        response = TipResponse.model_validate(tip)
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

