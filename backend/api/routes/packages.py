"""Packages routes - SQLAlchemy ORM"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from datetime import date
from sqlalchemy.orm import Session, joinedload

from database.session import get_db
from database.models import Package, Review, Destination

router = APIRouter()


@router.get("/")
async def list_packages(
    destination: Optional[str] = None,
    destination_id: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_duration: Optional[int] = None,
    max_duration: Optional[int] = None,
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    start_date: Optional[date] = None,
    sort_by: Optional[str] = Query(None, description="Sort: price_asc, price_desc, duration_asc, duration_desc, name_asc"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Search packages with filters"""
    query = (
        db.query(Package)
        .options(joinedload(Package.destination))
        .filter(Package.is_active == True)
    )

    # SQL-level filters
    if destination_id:
        query = query.filter(Package.destination_id == destination_id)
    if min_price is not None:
        query = query.filter(Package.price_per_person >= min_price)
    if max_price is not None:
        query = query.filter(Package.price_per_person <= max_price)
    if min_duration is not None:
        query = query.filter(Package.duration_days >= min_duration)
    if max_duration is not None:
        query = query.filter(Package.duration_days <= max_duration)
    if start_date:
        query = query.filter(Package.available_from <= start_date)
        query = query.filter(Package.available_to >= start_date)

    # Sorting
    sort_map = {
        "price_asc": Package.price_per_person.asc(),
        "price_desc": Package.price_per_person.desc(),
        "duration_asc": Package.duration_days.asc(),
        "duration_desc": Package.duration_days.desc(),
        "name_asc": Package.name.asc(),
    }
    order = sort_map.get(sort_by, Package.price_per_person.asc())
    query = query.order_by(order)

    # Fetch all matching rows (needed for Python-level filters)
    rows = query.all()

    # Python-level filter: destination text search (fallback when no destination_id)
    if destination and not destination_id:
        dest_lower = destination.lower()
        rows = [
            p for p in rows
            if p.destination and (
                dest_lower in (p.destination.name or "").lower()
                or dest_lower in (p.destination.city or "").lower()
                or dest_lower in (p.destination.country or "").lower()
            )
        ]

    # Python-level filter: tags (match on destination tags)
    if tags:
        tag_list = [t.strip().lower() for t in tags.split(",") if t.strip()]
        rows = [
            p for p in rows
            if p.destination and p.destination.tags and any(
                t in [x.lower() for x in p.destination.tags] for t in tag_list
            )
        ]

    # Total after all filters
    total = len(rows)

    # Pagination (applied after Python filters)
    paginated = rows[offset:offset + limit]
    packages = [p.to_dict_with_destination() for p in paginated]

    return {
        "packages": packages,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/featured")
async def get_featured_packages(
    limit: int = Query(6, ge=1, le=20),
    db: Session = Depends(get_db),
):
    """Get featured/popular packages"""
    rows = (
        db.query(Package)
        .options(joinedload(Package.destination))
        .filter(Package.is_active == True)
        .order_by(Package.price_per_person.desc())
        .limit(limit)
        .all()
    )
    packages = [p.to_dict_with_destination() for p in rows]
    return {"packages": packages}


@router.get("/{package_id}")
async def get_package(package_id: str, db: Session = Depends(get_db)):
    """Get package details with destination and reviews"""
    pkg = (
        db.query(Package)
        .options(joinedload(Package.destination))
        .filter(Package.id == package_id)
        .first()
    )

    if not pkg:
        raise HTTPException(status_code=404, detail="Package not found")

    package = pkg.to_dict_with_destination()

    # Get reviews with user info
    reviews = (
        db.query(Review)
        .options(joinedload(Review.user))
        .filter(Review.package_id == package_id)
        .order_by(Review.created_at.desc())
        .all()
    )
    package["reviews"] = [r.to_dict_with_user() for r in reviews]

    return package


@router.get("/{package_id}/availability")
async def check_availability(
    package_id: str,
    start_date: date,
    num_persons: int = Query(1, ge=1, le=10),
    db: Session = Depends(get_db),
):
    """Check package availability for a date"""
    pkg = db.query(Package).filter(Package.id == package_id).first()

    if not pkg:
        raise HTTPException(status_code=404, detail="Package not found")

    # Check date availability
    available_from = pkg.available_from
    available_to = pkg.available_to

    if available_from and available_to:
        if hasattr(available_from, 'date'):
            available_from = available_from.date()
        if hasattr(available_to, 'date'):
            available_to = available_to.date()

        if not (available_from <= start_date <= available_to):
            return {
                "available": False,
                "reason": "Date outside availability window"
            }

    if num_persons > pkg.max_persons:
        return {
            "available": False,
            "reason": f"Maximum {pkg.max_persons} persons allowed"
        }

    return {
        "available": True,
        "package_id": package_id,
        "start_date": str(start_date),
        "num_persons": num_persons,
        "price_per_person": float(pkg.price_per_person),
        "total_price": float(pkg.price_per_person) * num_persons
    }
