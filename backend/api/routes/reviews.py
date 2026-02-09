"""Reviews routes - Oracle"""

import uuid
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import Optional

from database.oracle_client import execute_query, execute_query_single, execute_insert, execute_update, execute_scalar
from database.queries import (
    REVIEWS_BY_PACKAGE, REVIEW_INSERT, REVIEW_CHECK_BOOKING,
    REVIEW_AVG_FOR_DESTINATION, DESTINATION_UPDATE_RATING,
    BOOKING_SIMPLE, PACKAGE_SIMPLE,
    format_review_with_user
)
from auth.middleware import get_current_user

router = APIRouter()


class ReviewCreate(BaseModel):
    package_id: str
    booking_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


@router.get("/package/{package_id}")
async def get_package_reviews(
    package_id: str,
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0)
):
    """Get reviews for a package"""
    rows = execute_query(REVIEWS_BY_PACKAGE, {
        "package_id": package_id,
        "offset": offset,
        "limit": limit
    })
    reviews = [format_review_with_user(r) for r in rows]
    return {"reviews": reviews}


@router.post("/")
async def create_review(
    review: ReviewCreate,
    user=Depends(get_current_user)
):
    """Create a review for a completed booking"""
    # Verify booking belongs to user and is completed
    booking = execute_query_single(BOOKING_SIMPLE, {
        "id": review.booking_id,
        "user_id": user.id
    })

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking["status"] != "completed":
        raise HTTPException(
            status_code=400,
            detail="Can only review completed bookings"
        )

    if booking["package_id"] != review.package_id:
        raise HTTPException(
            status_code=400,
            detail="Package doesn't match booking"
        )

    # Check if already reviewed
    existing = execute_query_single(REVIEW_CHECK_BOOKING, {
        "booking_id": review.booking_id
    })
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Already reviewed this booking"
        )

    review_id = str(uuid.uuid4())
    execute_insert(REVIEW_INSERT, {
        "id": review_id,
        "user_id": user.id,
        "package_id": review.package_id,
        "booking_id": review.booking_id,
        "rating": review.rating,
        "comment": review.comment
    })

    result = execute_query_single(
        "SELECT r.id, r.user_id, r.package_id, r.booking_id, r.rating, r.review_comment AS comment, r.created_at, r.updated_at, u.first_name, u.last_name, u.avatar_url FROM reviews r JOIN users u ON r.user_id = u.id WHERE r.id = :id",
        {"id": review_id}
    )
    result = format_review_with_user(result) if result else {"id": review_id}

    # Update destination average rating
    _update_destination_rating(review.package_id)

    return {"message": "Review created", "review": result}


def _update_destination_rating(package_id: str):
    """Update destination average rating after new review"""
    pkg = execute_query_single(PACKAGE_SIMPLE, {"id": package_id})
    if not pkg:
        return

    destination_id = pkg["destination_id"]

    avg = execute_scalar(REVIEW_AVG_FOR_DESTINATION, {"destination_id": destination_id})

    if avg is not None:
        execute_update(DESTINATION_UPDATE_RATING, {
            "average_rating": round(float(avg), 1),
            "id": destination_id
        })
