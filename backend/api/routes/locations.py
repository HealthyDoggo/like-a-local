"""Location API endpoints"""
from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from datetime import datetime

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
    category_id: Optional[str] = None

    model_config = {"from_attributes": True}


class CityInfo(BaseModel):
    """City information model"""
    name: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None


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
def get_countries_and_cities(
    db: Session = Depends(get_database)
):
    """
    Get comprehensive list of countries and their major cities.
    Includes coordinates for mapping and location selection.
    """
    # Load cities data from JSON file
    locations = db.query(Location).all()
    countries = []
    country_indices = {}
    for location in locations:
        if location.country not in country_indices:
            country_indices[location.country] = len(countries)
            countries.append(CountryInfo(name=location.country, code=location.country, cities=[]))
        countries[country_indices[location.country]].cities.append(CityInfo(name=location.name, latitude=location.latitude, longitude=location.longitude))
    return CountriesResponse(countries=countries)


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


@router.get("/{location_id}/category-counts")
def get_category_counts(
    location_id: int,
    db: Session = Depends(get_database)
) -> Dict[str, int]:
    """Get promoted tip counts per category for a location"""
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    # Count promoted tips instead of all tips to match what's displayed
    counts = db.query(
        TipPromotion.category_id,
        func.count(TipPromotion.id).label('count')
    ).filter(
        TipPromotion.location_id == location_id,
        TipPromotion.category_id.isnot(None)
    ).group_by(TipPromotion.category_id).all()

    return {category: count for category, count in counts}


@router.get("/{location_id}/promoted-tips", response_model=List[PromotedTipResponse])
def get_location_promoted_tips(
    location_id: int,
    category_id: Optional[str] = Query(None, description="Filter by category ID"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of tips to return"),
    db: Session = Depends(get_database)
):
    """Get promoted tips for a specific location, ranked by mention count"""
    location = db.query(Location).filter(Location.id == location_id).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    query = db.query(TipPromotion).filter(
        TipPromotion.location_id == location_id
    )

    if category_id:
        query = query.filter(TipPromotion.category_id == category_id)

    promoted_tips = query.order_by(TipPromotion.mention_count.desc()).limit(limit).all()

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
    category_id: Optional[str] = Query(None, description="Filter by category ID"),
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
    query = db.query(TipPromotion).filter(
        TipPromotion.location_id == location.id
    )

    if category_id:
        query = query.filter(TipPromotion.category_id == category_id)

    promoted_tips = query.order_by(TipPromotion.mention_count.desc()).limit(limit).all()

    results = []
    for tip in promoted_tips:
        response = PromotedTipResponse.model_validate(tip)
        response.location_name = location.name
        response.location_country = location.country
        results.append(response)

    return results

