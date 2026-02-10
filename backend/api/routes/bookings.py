"""Bookings routes - SQLAlchemy ORM"""

import uuid
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import date, timedelta
from sqlalchemy.orm import Session, joinedload

from database.session import get_db
from database.models import Booking, Package
from auth.middleware import get_current_user

router = APIRouter()


class BookingCreate(BaseModel):
    package_id: str
    start_date: date
    num_persons: int
    special_requests: Optional[str] = None


class BookingUpdate(BaseModel):
    status: Optional[str] = None
    special_requests: Optional[str] = None


def _get_booking_with_joins(db: Session, booking_id: str, user_id: str):
    """Helper to load a booking with package+destination joins."""
    return (
        db.query(Booking)
        .options(joinedload(Booking.package).joinedload(Package.destination))
        .filter(Booking.id == booking_id, Booking.user_id == user_id)
        .first()
    )


@router.get("/")
async def list_user_bookings(
    status: Optional[str] = None,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List current user's bookings"""
    query = (
        db.query(Booking)
        .options(joinedload(Booking.package).joinedload(Package.destination))
        .filter(Booking.user_id == user.id)
    )

    if status:
        query = query.filter(Booking.status == status)

    query = query.order_by(Booking.created_at.desc())

    rows = query.all()
    bookings = [b.to_dict_with_joins() for b in rows]
    return {"bookings": bookings}


@router.post("/")
async def create_booking(
    booking: BookingCreate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new booking"""
    pkg = db.query(Package).filter(Package.id == booking.package_id).first()

    if not pkg:
        raise HTTPException(status_code=404, detail="Package not found")

    # Validate date
    available_from = pkg.available_from
    available_to = pkg.available_to

    if available_from and available_to:
        if hasattr(available_from, 'date'):
            available_from = available_from.date()
        if hasattr(available_to, 'date'):
            available_to = available_to.date()

        if not (available_from <= booking.start_date <= available_to):
            raise HTTPException(
                status_code=400,
                detail="Date outside availability window"
            )

    if booking.num_persons > pkg.max_persons:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {pkg.max_persons} persons allowed"
        )

    end_date = booking.start_date + timedelta(days=pkg.duration_days)
    total_price = float(pkg.price_per_person) * booking.num_persons

    booking_id = str(uuid.uuid4())

    new_booking = Booking(
        id=booking_id,
        user_id=user.id,
        package_id=booking.package_id,
        start_date=booking.start_date,
        end_date=end_date,
        num_persons=booking.num_persons,
        total_price=total_price,
        special_requests=booking.special_requests,
        status="pending",
        payment_status="unpaid",
    )
    db.add(new_booking)
    db.commit()

    result = _get_booking_with_joins(db, booking_id, user.id)
    result_dict = result.to_dict_with_joins() if result else {"id": booking_id}

    return {
        "message": "Booking created successfully",
        "booking": result_dict
    }


@router.get("/{booking_id}")
async def get_booking(
    booking_id: str,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get booking details"""
    result = _get_booking_with_joins(db, booking_id, user.id)

    if not result:
        raise HTTPException(status_code=404, detail="Booking not found")

    return result.to_dict_with_joins()


@router.patch("/{booking_id}")
async def update_booking(
    booking_id: str,
    update: BookingUpdate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a booking"""
    existing = (
        db.query(Booking)
        .filter(Booking.id == booking_id, Booking.user_id == user.id)
        .first()
    )

    if not existing:
        raise HTTPException(status_code=404, detail="Booking not found")

    if existing.status not in ["pending"]:
        raise HTTPException(
            status_code=400,
            detail="Cannot update booking with this status"
        )

    if update.status:
        existing.status = update.status

    if update.special_requests is not None:
        existing.special_requests = update.special_requests

    db.commit()

    result = _get_booking_with_joins(db, booking_id, user.id)
    return {"message": "Booking updated", "booking": result.to_dict_with_joins()}


@router.delete("/{booking_id}")
async def cancel_booking(
    booking_id: str,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a booking"""
    existing = (
        db.query(Booking)
        .filter(Booking.id == booking_id, Booking.user_id == user.id)
        .first()
    )

    if not existing:
        raise HTTPException(status_code=404, detail="Booking not found")

    if existing.payment_status == "paid":
        raise HTTPException(
            status_code=400,
            detail="Cannot delete paid booking. Please contact support."
        )

    db.delete(existing)
    db.commit()

    return {"message": "Booking deleted"}
