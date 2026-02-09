"""Bookings routes - Oracle"""

import uuid
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import date, timedelta

from database.oracle_client import execute_query, execute_query_single, execute_insert, execute_update
from database.queries import (
    BOOKINGS_BY_USER, BOOKING_BY_ID, BOOKING_INSERT, BOOKING_UPDATE_STATUS,
    BOOKING_SIMPLE, PACKAGE_SIMPLE, format_booking_with_joins, format_package
)
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


@router.get("/")
async def list_user_bookings(
    status: Optional[str] = None,
    user=Depends(get_current_user)
):
    """List current user's bookings"""
    sql = BOOKINGS_BY_USER
    params = {"user_id": user.id}

    if status:
        sql += " AND b.status = :status"
        params["status"] = status

    sql += " ORDER BY b.created_at DESC"

    rows = execute_query(sql, params)
    bookings = [format_booking_with_joins(r) for r in rows]
    return {"bookings": bookings}


@router.post("/")
async def create_booking(
    booking: BookingCreate,
    user=Depends(get_current_user)
):
    """Create a new booking"""
    pkg = execute_query_single(PACKAGE_SIMPLE, {"id": booking.package_id})

    if not pkg:
        raise HTTPException(status_code=404, detail="Package not found")

    pkg = format_package(pkg)

    # Validate date
    available_from = pkg["available_from"]
    available_to = pkg["available_to"]

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

    if booking.num_persons > pkg["max_persons"]:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {pkg['max_persons']} persons allowed"
        )

    end_date = booking.start_date + timedelta(days=pkg["duration_days"])
    total_price = float(pkg["price_per_person"]) * booking.num_persons

    booking_id = str(uuid.uuid4())

    execute_insert(BOOKING_INSERT, {
        "id": booking_id,
        "user_id": user.id,
        "package_id": booking.package_id,
        "start_date": str(booking.start_date),
        "end_date": str(end_date),
        "num_persons": booking.num_persons,
        "total_price": total_price,
        "special_requests": booking.special_requests,
        "status": "pending",
        "payment_status": "unpaid"
    })

    result = execute_query_single(BOOKING_BY_ID, {"id": booking_id, "user_id": user.id})
    result = format_booking_with_joins(result) if result else {"id": booking_id}

    return {
        "message": "Booking created successfully",
        "booking": result
    }


@router.get("/{booking_id}")
async def get_booking(booking_id: str, user=Depends(get_current_user)):
    """Get booking details"""
    result = execute_query_single(BOOKING_BY_ID, {"id": booking_id, "user_id": user.id})

    if not result:
        raise HTTPException(status_code=404, detail="Booking not found")

    return format_booking_with_joins(result)


@router.patch("/{booking_id}")
async def update_booking(
    booking_id: str,
    update: BookingUpdate,
    user=Depends(get_current_user)
):
    """Update a booking"""
    existing = execute_query_single(BOOKING_SIMPLE, {"id": booking_id, "user_id": user.id})

    if not existing:
        raise HTTPException(status_code=404, detail="Booking not found")

    if existing["status"] not in ["pending"]:
        raise HTTPException(
            status_code=400,
            detail="Cannot update booking with this status"
        )

    if update.status:
        execute_update(BOOKING_UPDATE_STATUS, {"status": update.status, "id": booking_id})

    if update.special_requests is not None:
        execute_update(
            "UPDATE bookings SET special_requests = :special_requests WHERE id = :id",
            {"special_requests": update.special_requests, "id": booking_id}
        )

    result = execute_query_single(BOOKING_BY_ID, {"id": booking_id, "user_id": user.id})
    return {"message": "Booking updated", "booking": format_booking_with_joins(result)}


@router.delete("/{booking_id}")
async def cancel_booking(booking_id: str, user=Depends(get_current_user)):
    """Cancel a booking"""
    existing = execute_query_single(BOOKING_SIMPLE, {"id": booking_id, "user_id": user.id})

    if not existing:
        raise HTTPException(status_code=404, detail="Booking not found")

    if existing["payment_status"] == "paid":
        raise HTTPException(
            status_code=400,
            detail="Cannot cancel paid booking. Please contact support."
        )

    execute_update(BOOKING_UPDATE_STATUS, {"status": "cancelled", "id": booking_id})

    result = execute_query_single(BOOKING_BY_ID, {"id": booking_id, "user_id": user.id})
    return {"message": "Booking cancelled", "booking": format_booking_with_joins(result)}
