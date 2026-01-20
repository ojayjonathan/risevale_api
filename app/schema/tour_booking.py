from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel

from app.schema.setups import Country
from app.schema.tour import Tour


class BookingStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"

    def __str__(self):
        return self.value


class PaymentStatus(str, Enum):
    NOT_REQUIRED = "NOT_REQUIRED"
    PENDING = "PENDING"
    PAID = "PAID"
    FAILED = "FAILED"

    def __str__(self):
        return self.value


class TourBookingCreate(BaseModel):
    full_name: str
    email: str
    phone: str
    country_id: int
    travel_date: Optional[date] = None
    number_of_people: int
    special_requests: Optional[str] = None
    tour_id: int
    status: Optional[str] = None
    payment_status: Optional[str] = None


class TourBookingUpdate(BaseModel):
    status: Optional[str] = None
    payment_status: Optional[str] = None
    number_of_people: Optional[int] = None
    special_requests: Optional[str] = None


class TourBooking(BaseModel):
    id: int
    tour_id: int
    full_name: str
    email: str
    phone: str
    travel_date: Optional[date] = None
    number_of_people: int
    status: str
    payment_status: str
    tour: Tour

    country: Country

    class Config:
        from_attributes = True
