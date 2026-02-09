"""Destinations routes - Oracle"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from database.oracle_client import execute_query, execute_query_single
from database.queries import (
    DESTINATIONS_LIST, DESTINATIONS_BY_COUNTRY, DESTINATION_BY_ID,
    DESTINATION_PACKAGES, format_destination, format_package
)

router = APIRouter()


@router.get("/")
async def list_destinations(
    country: Optional[str] = None,
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    limit: int = Query(20, ge=1, le=100)
):
    """List all destinations with optional filters"""
    if country:
        rows = execute_query(DESTINATIONS_BY_COUNTRY, {
            "country": country,
            "offset": 0,
            "limit": limit
        })
    else:
        rows = execute_query(DESTINATIONS_LIST, {
            "offset": 0,
            "limit": limit
        })

    destinations = [format_destination(r) for r in rows]

    # Filter by tags in Python (JSON array in CLOB)
    if tags:
        tag_list = [t.strip().lower() for t in tags.split(",")]
        destinations = [
            d for d in destinations
            if d.get("tags") and any(
                t.lower() in [x.lower() for x in d["tags"]] for t in tag_list
            )
        ]

    return {"destinations": destinations, "count": len(destinations)}


@router.get("/{destination_id}")
async def get_destination(destination_id: str):
    """Get destination details with its packages"""
    dest = execute_query_single(DESTINATION_BY_ID, {"id": destination_id})

    if not dest:
        raise HTTPException(status_code=404, detail="Destination not found")

    dest = format_destination(dest)

    # Get packages for this destination
    pkg_rows = execute_query(DESTINATION_PACKAGES, {"destination_id": destination_id})
    dest["packages"] = [format_package(p) for p in pkg_rows]

    return dest


@router.get("/{destination_id}/packages")
async def get_destination_packages(
    destination_id: str,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
):
    """Get packages for a specific destination"""
    sql = """
        SELECT * FROM packages
        WHERE destination_id = :destination_id AND is_active = 1
    """
    params = {"destination_id": destination_id}

    if min_price is not None:
        sql += " AND price_per_person >= :min_price"
        params["min_price"] = min_price
    if max_price is not None:
        sql += " AND price_per_person <= :max_price"
        params["max_price"] = max_price

    sql += " ORDER BY price_per_person"

    rows = execute_query(sql, params)
    packages = [format_package(r) for r in rows]

    return {"packages": packages, "count": len(packages)}
