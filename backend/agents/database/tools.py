"""Database Agent Tools - CRUD operations for VacanceAI (Oracle)"""

import uuid
from langchain_core.tools import tool
from typing import Optional, List
from datetime import datetime, timedelta

from database.oracle_client import execute_query, execute_query_single, execute_insert
from database.queries import (
    PACKAGES_LIST_BASE, PACKAGE_BY_ID, PACKAGE_SIMPLE,
    BOOKINGS_BY_USER, FAVORITES_BY_USER, FAVORITE_CHECK,
    FAVORITE_INSERT, FAVORITE_DELETE, BOOKING_INSERT,
    format_package_with_destination, format_package,
    format_review_with_user, format_booking_with_joins,
    format_favorite_with_joins, format_destination,
    parse_json_field
)
from database.oracle_client import execute_delete


@tool
def search_packages(
    destination: Optional[str] = None,
    country: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_duration: Optional[int] = None,
    max_duration: Optional[int] = None,
    tags: Optional[List[str]] = None,
    start_date: Optional[str] = None,
    limit: int = 10
) -> list:
    """Search vacation packages with various filters.

    Args:
        destination: Destination name to search for
        country: Country to filter by
        min_price: Minimum price per person
        max_price: Maximum price per person
        min_duration: Minimum duration in days
        max_duration: Maximum duration in days
        tags: List of tags (beach, mountain, city, adventure, romantic, family, luxury)
        start_date: Travel date (YYYY-MM-DD format)
        limit: Maximum results to return

    Returns:
        List of matching packages with destination details
    """
    sql = PACKAGES_LIST_BASE
    params = {}

    if min_price:
        sql += " AND p.price_per_person >= :min_price"
        params["min_price"] = min_price
    if max_price:
        sql += " AND p.price_per_person <= :max_price"
        params["max_price"] = max_price
    if min_duration:
        sql += " AND p.duration_days >= :min_duration"
        params["min_duration"] = min_duration
    if max_duration:
        sql += " AND p.duration_days <= :max_duration"
        params["max_duration"] = max_duration
    if start_date:
        sql += " AND p.available_from <= TO_DATE(:start_date, 'YYYY-MM-DD')"
        sql += " AND p.available_to >= TO_DATE(:start_date, 'YYYY-MM-DD')"
        params["start_date"] = start_date

    sql += " ORDER BY p.price_per_person"
    sql += " OFFSET 0 ROWS FETCH NEXT :limit ROWS ONLY"
    params["limit"] = limit

    rows = execute_query(sql, params)
    packages = [format_package_with_destination(r) for r in rows]

    # Filter by destination/country in Python
    if destination:
        destination_lower = destination.lower()
        packages = [
            p for p in packages
            if destination_lower in (p.get("destinations", {}).get("name", "") or "").lower()
            or destination_lower in (p.get("destinations", {}).get("city", "") or "").lower()
        ]

    if country:
        country_lower = country.lower()
        packages = [
            p for p in packages
            if country_lower in (p.get("destinations", {}).get("country", "") or "").lower()
        ]

    if tags:
        packages = [
            p for p in packages
            if any(
                tag.lower() in [x.lower() for x in (p.get("destinations", {}).get("tags") or [])]
                for tag in tags
            )
        ]

    return packages[:limit]


@tool
def get_package_details(package_id: str) -> dict:
    """Get complete details for a specific package.

    Args:
        package_id: UUID of the package

    Returns:
        Package details with destination and reviews
    """
    row = execute_query_single(PACKAGE_BY_ID, {"id": package_id})

    if not row:
        return {"error": "Package not found"}

    package = format_package_with_destination(row)

    # Get reviews
    review_rows = execute_query(
        "SELECT r.id, r.user_id, r.package_id, r.booking_id, r.rating, r.review_comment AS comment, r.created_at, r.updated_at, u.first_name, u.last_name FROM reviews r JOIN users u ON r.user_id = u.id WHERE r.package_id = :package_id ORDER BY r.created_at DESC",
        {"package_id": package_id}
    )
    package["reviews"] = [format_review_with_user(r) for r in review_rows]

    return package


@tool
def get_destinations(
    country: Optional[str] = None,
    tags: Optional[List[str]] = None,
    limit: int = 10
) -> list:
    """List available destinations.

    Args:
        country: Filter by country
        tags: Filter by tags
        limit: Maximum results

    Returns:
        List of destinations
    """
    sql = "SELECT * FROM destinations"
    params = {}

    if country:
        sql += " WHERE UPPER(country) LIKE UPPER(:country)"
        params["country"] = f"%{country}%"

    sql += " ORDER BY average_rating DESC NULLS LAST"
    sql += " OFFSET 0 ROWS FETCH NEXT :limit ROWS ONLY"
    params["limit"] = limit

    rows = execute_query(sql, params)
    destinations = [format_destination(r) for r in rows]

    if tags:
        destinations = [
            d for d in destinations
            if any(
                tag.lower() in [x.lower() for x in (d.get("tags") or [])]
                for tag in tags
            )
        ]

    return destinations


@tool
def create_booking(
    user_id: str,
    package_id: str,
    start_date: str,
    num_persons: int,
    special_requests: Optional[str] = None
) -> dict:
    """Create a new booking for a user.

    Args:
        user_id: UUID of the user
        package_id: UUID of the package
        start_date: Start date (YYYY-MM-DD)
        num_persons: Number of travelers
        special_requests: Optional special requests

    Returns:
        Created booking details or error
    """
    pkg = execute_query_single(PACKAGE_SIMPLE, {"id": package_id})

    if not pkg:
        return {"error": "Package not found"}

    pkg = format_package(pkg)

    if num_persons > pkg["max_persons"]:
        return {"error": f"Maximum {pkg['max_persons']} persons allowed"}

    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = start + timedelta(days=pkg["duration_days"])
    total_price = float(pkg["price_per_person"]) * num_persons

    booking_id = str(uuid.uuid4())

    execute_insert(BOOKING_INSERT, {
        "id": booking_id,
        "user_id": user_id,
        "package_id": package_id,
        "start_date": start_date,
        "end_date": end.strftime("%Y-%m-%d"),
        "num_persons": num_persons,
        "total_price": total_price,
        "special_requests": special_requests,
        "status": "pending",
        "payment_status": "unpaid"
    })

    return {
        "success": True,
        "booking": {"id": booking_id, "total_price": total_price, "status": "pending"},
        "message": f"Booking created! Total: {total_price}€"
    }


@tool
def get_user_bookings(
    user_id: str,
    status: Optional[str] = None
) -> list:
    """Get all bookings for a user.

    Args:
        user_id: UUID of the user
        status: Optional status filter (pending, confirmed, cancelled, completed)

    Returns:
        List of user's bookings
    """
    sql = BOOKINGS_BY_USER
    params = {"user_id": user_id}

    if status:
        sql += " AND b.status = :status"
        params["status"] = status

    sql += " ORDER BY b.created_at DESC"

    rows = execute_query(sql, params)
    return [format_booking_with_joins(r) for r in rows]


@tool
def add_to_favorites(user_id: str, package_id: str) -> dict:
    """Add a package to user's favorites.

    Args:
        user_id: UUID of the user
        package_id: UUID of the package

    Returns:
        Result of the operation
    """
    existing = execute_query_single(FAVORITE_CHECK, {
        "user_id": user_id,
        "package_id": package_id
    })

    if existing:
        return {"success": False, "message": "Already in favorites"}

    execute_insert(FAVORITE_INSERT, {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "package_id": package_id
    })

    return {"success": True, "message": "Added to favorites"}


@tool
def get_user_favorites(user_id: str) -> list:
    """Get user's favorite packages.

    Args:
        user_id: UUID of the user

    Returns:
        List of favorite packages
    """
    rows = execute_query(FAVORITES_BY_USER, {"user_id": user_id})
    return [format_favorite_with_joins(r) for r in rows]


@tool
def remove_from_favorites(user_id: str, package_id: str) -> dict:
    """Remove a package from user's favorites.

    Args:
        user_id: UUID of the user
        package_id: UUID of the package

    Returns:
        Result of the operation
    """
    count = execute_delete(FAVORITE_DELETE, {
        "user_id": user_id,
        "package_id": package_id
    })

    if count > 0:
        return {"success": True, "message": "Removed from favorites"}

    return {"success": False, "message": "Favorite not found"}
