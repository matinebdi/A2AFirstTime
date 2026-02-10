"""TripAdvisor routes - SQLAlchemy ORM"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from sqlalchemy.orm import Session

from database.session import get_db
from database.models import TripAdvisorLocation, TripAdvisorPhoto, TripAdvisorReview

router = APIRouter()


@router.get("/locations")
async def list_locations(
    country: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List TripAdvisor locations"""
    query = db.query(TripAdvisorLocation)
    if country:
        query = query.filter(TripAdvisorLocation.search_country == country)
    rows = query.order_by(TripAdvisorLocation.name).all()
    locations = [r.to_dict() for r in rows]
    return {"locations": locations}


@router.get("/countries")
async def list_countries(db: Session = Depends(get_db)):
    """List unique countries from TripAdvisor locations"""
    rows = (
        db.query(TripAdvisorLocation.search_country)
        .filter(TripAdvisorLocation.search_country.isnot(None))
        .distinct()
        .order_by(TripAdvisorLocation.search_country)
        .all()
    )
    countries = [r[0] for r in rows]
    return {"countries": countries}


@router.get("/locations/{location_id}")
async def get_location(location_id: str, db: Session = Depends(get_db)):
    """Get a single TripAdvisor location"""
    row = (
        db.query(TripAdvisorLocation)
        .filter(TripAdvisorLocation.location_id == location_id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Location not found")
    return row.to_dict()


@router.get("/locations/{location_id}/photos")
async def get_location_photos(location_id: str, db: Session = Depends(get_db)):
    """Get photos for a TripAdvisor location"""
    rows = (
        db.query(TripAdvisorPhoto)
        .filter(TripAdvisorPhoto.location_id == location_id)
        .all()
    )
    photos = [r.to_dict() for r in rows]
    return {"photos": photos}


@router.get("/locations/{location_id}/reviews")
async def get_location_reviews(location_id: str, db: Session = Depends(get_db)):
    """Get reviews for a TripAdvisor location"""
    rows = (
        db.query(TripAdvisorReview)
        .filter(TripAdvisorReview.location_id == location_id)
        .order_by(TripAdvisorReview.published_date.desc().nulls_last())
        .all()
    )
    reviews = [r.to_dict() for r in rows]
    return {"reviews": reviews}
