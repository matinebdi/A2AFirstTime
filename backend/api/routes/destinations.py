"""Destinations routes - SQLAlchemy ORM"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from sqlalchemy.orm import Session

from database.session import get_db
from database.models import Destination, Package

router = APIRouter()


@router.get("/")
async def list_destinations(
    country: Optional[str] = None,
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List all destinations with optional filters"""
    query = db.query(Destination)

    if country:
        query = query.filter(Destination.country == country)

    query = query.order_by(Destination.average_rating.desc().nulls_last())

    rows = query.offset(0).limit(limit).all()
    destinations = [d.to_dict() for d in rows]

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
async def get_destination(destination_id: str, db: Session = Depends(get_db)):
    """Get destination details with its packages"""
    dest = db.query(Destination).filter(Destination.id == destination_id).first()

    if not dest:
        raise HTTPException(status_code=404, detail="Destination not found")

    d = dest.to_dict()

    # Get packages for this destination
    pkgs = (
        db.query(Package)
        .filter(Package.destination_id == destination_id, Package.is_active == True)
        .order_by(Package.price_per_person)
        .all()
    )
    d["packages"] = [p.to_dict() for p in pkgs]

    return d


@router.get("/{destination_id}/packages")
async def get_destination_packages(
    destination_id: str,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    db: Session = Depends(get_db),
):
    """Get packages for a specific destination"""
    query = (
        db.query(Package)
        .filter(Package.destination_id == destination_id, Package.is_active == True)
    )

    if min_price is not None:
        query = query.filter(Package.price_per_person >= min_price)
    if max_price is not None:
        query = query.filter(Package.price_per_person <= max_price)

    query = query.order_by(Package.price_per_person)

    rows = query.all()
    packages = [p.to_dict() for p in rows]

    return {"packages": packages, "count": len(packages)}
