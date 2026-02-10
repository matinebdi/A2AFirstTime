"""Reviews routes - SQLAlchemy ORM"""

import uuid
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from database.session import get_db
from database.models import Review, Booking, Package, Destination
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
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Get reviews for a package"""
    rows = (
        db.query(Review)
        .options(joinedload(Review.user))
        .filter(Review.package_id == package_id)
        .order_by(Review.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    reviews = [r.to_dict_with_user() for r in rows]
    return {"reviews": reviews}


@router.post("/")
async def create_review(
    review: ReviewCreate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a review for a completed booking"""
    booking = (
        db.query(Booking)
        .filter(Booking.id == review.booking_id, Booking.user_id == user.id)
        .first()
    )

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.status != "completed":
        raise HTTPException(
            status_code=400,
            detail="Can only review completed bookings"
        )

    if booking.package_id != review.package_id:
        raise HTTPException(
            status_code=400,
            detail="Package doesn't match booking"
        )

    existing = db.query(Review).filter(Review.booking_id == review.booking_id).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Already reviewed this booking"
        )

    review_id = str(uuid.uuid4())
    new_review = Review(
        id=review_id,
        user_id=user.id,
        package_id=review.package_id,
        booking_id=review.booking_id,
        rating=review.rating,
        review_comment=review.comment,
    )
    db.add(new_review)
    db.commit()

    # Reload with user join
    result = (
        db.query(Review)
        .options(joinedload(Review.user))
        .filter(Review.id == review_id)
        .first()
    )
    result_dict = result.to_dict_with_user() if result else {"id": review_id}

    # Update destination average rating
    _update_destination_rating(db, review.package_id)

    return {"message": "Review created", "review": result_dict}


def _update_destination_rating(db: Session, package_id: str):
    """Update destination average rating after new review"""
    pkg = db.query(Package).filter(Package.id == package_id).first()
    if not pkg:
        return

    avg = (
        db.query(func.avg(Review.rating))
        .join(Package, Review.package_id == Package.id)
        .filter(Package.destination_id == pkg.destination_id)
        .scalar()
    )

    if avg is not None:
        dest = db.query(Destination).filter(Destination.id == pkg.destination_id).first()
        if dest:
            dest.average_rating = round(float(avg), 1)
            db.commit()
