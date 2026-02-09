"""Packages routes - Oracle"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import date

from database.oracle_client import execute_query, execute_query_single
from database.queries import (
    PACKAGES_LIST_BASE, PACKAGE_BY_ID, PACKAGE_SIMPLE,
    PACKAGE_REVIEWS_WITH_USERS,
    format_package_with_destination, format_package, format_review_with_user
)

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
    offset: int = Query(0, ge=0)
):
    """Search packages with filters"""
    sql = PACKAGES_LIST_BASE
    params = {}

    if min_price is not None:
        sql += " AND p.price_per_person >= :min_price"
        params["min_price"] = min_price
    if max_price is not None:
        sql += " AND p.price_per_person <= :max_price"
        params["max_price"] = max_price
    if min_duration is not None:
        sql += " AND p.duration_days >= :min_duration"
        params["min_duration"] = min_duration
    if max_duration is not None:
        sql += " AND p.duration_days <= :max_duration"
        params["max_duration"] = max_duration
    if start_date:
        sql += " AND p.available_from <= TO_DATE(:start_date, 'YYYY-MM-DD')"
        sql += " AND p.available_to >= TO_DATE(:start_date, 'YYYY-MM-DD')"
        params["start_date"] = str(start_date)

    # Count total before pagination
    count_sql = f"SELECT COUNT(*) FROM ({sql})"
    from database.oracle_client import execute_scalar
    total = execute_scalar(count_sql, params) or 0

    # Add ordering and pagination
    sql += " ORDER BY p.price_per_person"
    sql += " OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY"
    params["offset"] = offset
    params["limit"] = limit

    rows = execute_query(sql, params)
    packages = [format_package_with_destination(r) for r in rows]

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
async def get_featured_packages(limit: int = Query(6, ge=1, le=20)):
    """Get featured/popular packages"""
    sql = PACKAGES_LIST_BASE + " ORDER BY p.created_at DESC OFFSET 0 ROWS FETCH NEXT :limit ROWS ONLY"
    rows = execute_query(sql, {"limit": limit})
    packages = [format_package_with_destination(r) for r in rows]
    return {"packages": packages}


@router.get("/{package_id}")
async def get_package(package_id: str):
    """Get package details with destination and reviews"""
    row = execute_query_single(PACKAGE_BY_ID, {"id": package_id})

    if not row:
        raise HTTPException(status_code=404, detail="Package not found")

    package = format_package_with_destination(row)

    # Get reviews with user info
    review_rows = execute_query(PACKAGE_REVIEWS_WITH_USERS, {"package_id": package_id})
    package["reviews"] = [format_review_with_user(r) for r in review_rows]

    return package


@router.get("/{package_id}/availability")
async def check_availability(
    package_id: str,
    start_date: date,
    num_persons: int = Query(1, ge=1, le=10)
):
    """Check package availability for a date"""
    pkg = execute_query_single(PACKAGE_SIMPLE, {"id": package_id})

    if not pkg:
        raise HTTPException(status_code=404, detail="Package not found")

    pkg = format_package(pkg)

    # Check date availability
    available_from = pkg["available_from"]
    available_to = pkg["available_to"]

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

    if num_persons > pkg["max_persons"]:
        return {
            "available": False,
            "reason": f"Maximum {pkg['max_persons']} persons allowed"
        }

    return {
        "available": True,
        "package_id": package_id,
        "start_date": str(start_date),
        "num_persons": num_persons,
        "price_per_person": float(pkg["price_per_person"]),
        "total_price": float(pkg["price_per_person"]) * num_persons
    }
