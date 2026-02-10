"""Packages routes - SQLAlchemy ORM"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from datetime import date
from sqlalchemy.orm import Session, joinedload

from database.session import get_db
from database.models import Package, Review

router = APIRouter()


@router.get("/")
async def list_packages(
    destination: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_duration: Optional[int] = None,
    max_duration: Optional[int] = None,
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    start_date: Optional[date] = None,
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

    # Count total before pagination
    total = query.count()

    # Add ordering and pagination
    rows = (
        query.order_by(Package.price_per_person)
        .offset(offset)
        .limit(limit)
        .all()
    )

    packages = [p.to_dict_with_destination() for p in rows]

    # Filter by destination name in Python (from joined data)
    if destination:
        dest_lower = destination.lower()
        packages = [
            p for p in packages
            if dest_lower in (p.get("destinations", {}).get("name", "") or "").lower()
            or dest_lower in (p.get("destinations", {}).get("city", "") or "").lower()
        ]

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
