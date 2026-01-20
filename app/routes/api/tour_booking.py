# app/routes/tour_booking.py
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repository.tour_booking_repository import tour_booking
from app.routes.deps import current_user
from app.schema import Pagination
from app.schema.tour_booking import (
    TourBookingCreate,
    TourBooking,
    TourBookingUpdate,
)

router = APIRouter(prefix="/bookings", tags=["Tour Bookings"])


@router.post("/", response_model=TourBooking, status_code=201)
def create_booking(payload: TourBookingCreate, db: Session = Depends(get_db)):
    result = tour_booking.create(db, payload)
    return result


@router.get("/", response_model=Pagination[TourBooking])
def list_bookings(
    db: Session = Depends(get_db),
    country_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[str] = Query(None),
    payment_status: Optional[str] = Query(None),
    _user=Depends(current_user),
):
    filters = {}
    if country_id:
        filters["country_id"] = country_id
    if status:
        filters["status"] = status

    if payment_status:
        filters["payment_status"] = payment_status

    return tour_booking.get_all_paginated(db, page=page, limit=limit, **filters)


@router.put("/{booking_id}", response_model=TourBooking)
def update_booking(
    booking_id: int,
    payload: TourBookingUpdate,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    return tour_booking.update(
        db,
        current_item=tour_booking.get_object_or_404(db=db, id=booking_id),
        item_in=payload,
        audit_user_id=user.id,
    )
