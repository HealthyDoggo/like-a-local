"""Location API endpoints"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.database.models import Location, Tip
from backend.api.dependencies import get_database
from backend.api.routes.tips import TipResponse

router = APIRouter(prefix="/api/locations", tags=["locations"])


class LocationResponse(BaseModel):
    """Location response model"""
    id: int
    name: str
    country: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    model_config = {"from_attributes": True}


@router.get("", response_model=List[LocationResponse])
def get_locations(
    db: Session = Depends(get_database)
):
    """Get all locations"""
    locations = db.query(Location).all()
    return [LocationResponse.model_validate(loc) for loc in locations]


@router.get("/{location_id}", response_model=LocationResponse)
def get_location(
    location_id: int,
    db: Session = Depends(get_database)
):
    """Get a specific location by ID"""
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return LocationResponse.model_validate(location)


@router.get("/{location_id}/tips", response_model=List[TipResponse])
def get_location_tips(
    location_id: int,
    db: Session = Depends(get_database)
):
    """Get tips for a specific location"""
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    tips = db.query(Tip).filter(Tip.location_id == location_id).order_by(Tip.submitted_at.desc()).all()
    
    results = []
    for tip in tips:
        response = TipResponse.model_validate(tip)
        response.location_name = location.name
        response.location_country = location.country
        results.append(response)
    
    return results

