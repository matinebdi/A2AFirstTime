"""TripAdvisor routes - Oracle"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from database.oracle_client import execute_query, execute_query_single
from database.queries import (
    TA_LOCATIONS_LIST, TA_LOCATIONS_BY_COUNTRY, TA_LOCATION_BY_ID,
    TA_PHOTOS_BY_LOCATION, TA_REVIEWS_BY_LOCATION, TA_COUNTRIES,
    format_ta_location, format_ta_photo
)

router = APIRouter()


@router.get("/locations")
async def list_locations(country: Optional[str] = None):
    """List TripAdvisor locations"""
    if country:
        rows = execute_query(TA_LOCATIONS_BY_COUNTRY, {"country": country})
    else:
        rows = execute_query(TA_LOCATIONS_LIST)

    locations = [format_ta_location(r) for r in rows]
    return {"locations": locations}


@router.get("/countries")
async def list_countries():
    """List unique countries from TripAdvisor locations"""
    rows = execute_query(TA_COUNTRIES)
    countries = [r["search_country"] for r in rows if r.get("search_country")]
    return {"countries": countries}


@router.get("/locations/{location_id}")
async def get_location(location_id: str):
    """Get a single TripAdvisor location"""
    row = execute_query_single(TA_LOCATION_BY_ID, {"location_id": location_id})
    if not row:
        raise HTTPException(status_code=404, detail="Location not found")
    return format_ta_location(row)


@router.get("/locations/{location_id}/photos")
async def get_location_photos(location_id: str):
    """Get photos for a TripAdvisor location"""
    rows = execute_query(TA_PHOTOS_BY_LOCATION, {"location_id": location_id})
    photos = [format_ta_photo(r) for r in rows]
    return {"photos": photos}


@router.get("/locations/{location_id}/reviews")
async def get_location_reviews(location_id: str):
    """Get reviews for a TripAdvisor location"""
    rows = execute_query(TA_REVIEWS_BY_LOCATION, {"location_id": location_id})
    # Alias 'username' to 'user_name' for frontend compatibility
    for r in rows:
        if "username" in r:
            r["user_name"] = r.pop("username")
    return {"reviews": rows}
