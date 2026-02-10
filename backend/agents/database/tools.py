"""Database Agent Tools - CRUD operations for VacanceAI (SQLAlchemy ORM)"""

import uuid
from langchain_core.tools import tool
from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import joinedload

from database.session import create_session
from database.models import (
    Package, Destination, Booking, Favorite, Review,
)


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
    db = create_session()
    try:
        query = (
            db.query(Package)
            .options(joinedload(Package.destination))
            .filter(Package.is_active == True)
        )

        if min_price:
            query = query.filter(Package.price_per_person >= min_price)
        if max_price:
            query = query.filter(Package.price_per_person <= max_price)
        if min_duration:
            query = query.filter(Package.duration_days >= min_duration)
        if max_duration:
            query = query.filter(Package.duration_days <= max_duration)
        if start_date:
            from sqlalchemy import func
            date_val = func.to_date(start_date, 'YYYY-MM-DD')
            query = query.filter(Package.available_from <= date_val)
            query = query.filter(Package.available_to >= date_val)

        rows = query.order_by(Package.price_per_person).limit(limit).all()
        packages = [p.to_dict_with_destination() for p in rows]
    finally:
        db.close()

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
    db = create_session()
    try:
        pkg = (
            db.query(Package)
            .options(joinedload(Package.destination))
            .filter(Package.id == package_id)
            .first()
        )

        if not pkg:
            return {"error": "Package not found"}

        package = pkg.to_dict_with_destination()

        # Get reviews
        reviews = (
            db.query(Review)
            .options(joinedload(Review.user))
            .filter(Review.package_id == package_id)
            .order_by(Review.created_at.desc())
            .all()
        )
        package["reviews"] = [r.to_dict_with_user() for r in reviews]

        return package
    finally:
        db.close()


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
    db = create_session()
    try:
        query = db.query(Destination)

        if country:
            query = query.filter(Destination.country.ilike(f"%{country}%"))

        rows = (
            query.order_by(Destination.average_rating.desc().nulls_last())
            .limit(limit)
            .all()
        )
        destinations = [d.to_dict() for d in rows]
    finally:
        db.close()

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
    db = create_session()
    try:
        pkg = db.query(Package).filter(Package.id == package_id).first()

        if not pkg:
            return {"error": "Package not found"}

        if num_persons > pkg.max_persons:
            return {"error": f"Maximum {pkg.max_persons} persons allowed"}

        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = start + timedelta(days=pkg.duration_days)
        total_price = float(pkg.price_per_person) * num_persons

        booking_id = str(uuid.uuid4())

        new_booking = Booking(
            id=booking_id,
            user_id=user_id,
            package_id=package_id,
            start_date=start.date(),
            end_date=end.date(),
            num_persons=num_persons,
            total_price=total_price,
            special_requests=special_requests,
            status="pending",
            payment_status="unpaid",
        )
        db.add(new_booking)
        db.commit()

        return {
            "success": True,
            "booking": {"id": booking_id, "total_price": total_price, "status": "pending"},
            "message": f"Booking created! Total: {total_price}€"
        }
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()


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
    db = create_session()
    try:
        query = (
            db.query(Booking)
            .options(joinedload(Booking.package).joinedload(Package.destination))
            .filter(Booking.user_id == user_id)
        )

        if status:
            query = query.filter(Booking.status == status)

        query = query.order_by(Booking.created_at.desc())
        rows = query.all()
        return [b.to_dict_with_joins() for b in rows]
    finally:
        db.close()


@tool
def add_to_favorites(user_id: str, package_id: str) -> dict:
    """Add a package to user's favorites.

    Args:
        user_id: UUID of the user
        package_id: UUID of the package

    Returns:
        Result of the operation
    """
    db = create_session()
    try:
        existing = (
            db.query(Favorite)
            .filter(Favorite.user_id == user_id, Favorite.package_id == package_id)
            .first()
        )

        if existing:
            return {"success": False, "message": "Already in favorites"}

        fav = Favorite(id=str(uuid.uuid4()), user_id=user_id, package_id=package_id)
        db.add(fav)
        db.commit()

        return {"success": True, "message": "Added to favorites"}
    except Exception as e:
        db.rollback()
        return {"success": False, "message": str(e)}
    finally:
        db.close()


@tool
def get_user_favorites(user_id: str) -> list:
    """Get user's favorite packages.

    Args:
        user_id: UUID of the user

    Returns:
        List of favorite packages
    """
    db = create_session()
    try:
        rows = (
            db.query(Favorite)
            .options(joinedload(Favorite.package).joinedload(Package.destination))
            .filter(Favorite.user_id == user_id)
            .all()
        )
        return [f.to_dict_with_joins() for f in rows]
    finally:
        db.close()


@tool
def remove_from_favorites(user_id: str, package_id: str) -> dict:
    """Remove a package from user's favorites.

    Args:
        user_id: UUID of the user
        package_id: UUID of the package

    Returns:
        Result of the operation
    """
    db = create_session()
    try:
        count = (
            db.query(Favorite)
            .filter(Favorite.user_id == user_id, Favorite.package_id == package_id)
            .delete()
        )
        db.commit()

        if count > 0:
            return {"success": True, "message": "Removed from favorites"}

        return {"success": False, "message": "Favorite not found"}
    finally:
        db.close()
