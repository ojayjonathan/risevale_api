from typing import Optional

from sqlalchemy.orm import Session

from app import schema
from app.models.tour_booking import TourBooking
from app.repository import BaseRepository
from app.repository.base import Model
from app.schema import TourBookingCreate
from app.schema.tour_booking import PaymentStatus, BookingStatus


class TourBookingRepository(
    BaseRepository[schema.TourBooking, TourBookingCreate, None]
):

    def __init__(self):
        super().__init__(TourBooking)

    def create(
        self,
        db: Session,
        item: TourBookingCreate,
        audit_user_id: Optional[int] = None,
    ) -> Model:
        item.payment_status = PaymentStatus.PENDING
        item.status = BookingStatus.PENDING

        return super().create(db, item, audit_user_id)


tour_booking = TourBookingRepository()
