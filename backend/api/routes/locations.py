"""Location API endpoints"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
import json
import os

from backend.database.models import Location, Tip, TipPromotion
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


class PromotedTipResponse(BaseModel):
    """Promoted tip response model"""
    id: int
    tip_text: str
    location_id: int
    location_name: Optional[str] = None
    location_country: Optional[str] = None
    mention_count: int
    similarity_score: Optional[float] = None
    promoted_at: datetime

    model_config = {"from_attributes": True}


class CityInfo(BaseModel):
    """City information model"""
    name: str
    latitude: float
    longitude: float


class CountryInfo(BaseModel):
    """Country information model"""
    name: str
    code: str
    cities: List[CityInfo]


class CountriesResponse(BaseModel):
    """Countries and cities response model"""
    countries: List[CountryInfo]


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


@router.get("/search", response_model=Optional[LocationResponse])
def search_location(
    name: str = Query(..., description="Location name"),
    country: str = Query(..., description="Country name"),
    db: Session = Depends(get_database)
):
    """Search for a location by name and country"""
    location = db.query(Location).filter(
        Location.name == name,
        Location.country == country
    ).first()

    if not location:
        return None

    return LocationResponse.model_validate(location)


@router.get("/countries-cities", response_model=CountriesResponse)
def get_countries_and_cities():
    """
    Get comprehensive list of countries and their major cities.
    Includes coordinates for mapping and location selection.
    """
    # Load cities data from JSON file
    data_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "data",
        "cities.json"
    )

    try:
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return CountriesResponse(**data)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Cities data file not found")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error parsing cities data")


@router.get("/{location_id}/promoted-tips", response_model=List[PromotedTipResponse])
def get_location_promoted_tips(
    location_id: int,
    limit: int = Query(20, ge=1, le=100, description="Maximum number of tips to return"),
    db: Session = Depends(get_database)
):
    """Get promoted tips for a specific location, ranked by mention count"""
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    promoted_tips = db.query(TipPromotion).filter(
        TipPromotion.location_id == location_id
    ).order_by(TipPromotion.mention_count.desc()).limit(limit).all()

    results = []
    for tip in promoted_tips:
        response = PromotedTipResponse.model_validate(tip)
        response.location_name = location.name
        response.location_country = location.country
        results.append(response)

    return results


# Convenience router for promoted tips (alternative to going through locations)
promoted_router = APIRouter(prefix="/api/promoted-tips", tags=["promoted-tips"])


@promoted_router.get("", response_model=List[PromotedTipResponse])
def get_promoted_tips_by_location_name(
    location_name: str = Query(..., description="Location name"),
    location_country: str = Query(..., description="Country name"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of tips to return"),
    db: Session = Depends(get_database)
):
    """
    Get promoted tips by location name and country (convenience endpoint).
    This combines location search and promoted tips retrieval in one call.
    """
    # Find location
    location = db.query(Location).filter(
        Location.name == location_name,
        Location.country == location_country
    ).first()

    if not location:
        # Return empty list if location not found (not an error - just no tips yet)
        return []

    # Get promoted tips
    promoted_tips = db.query(TipPromotion).filter(
        TipPromotion.location_id == location.id
    ).order_by(TipPromotion.mention_count.desc()).limit(limit).all()

    results = []
    for tip in promoted_tips:
        response = PromotedTipResponse.model_validate(tip)
        response.location_name = location.name
        response.location_country = location.country
        results.append(response)

    return results

