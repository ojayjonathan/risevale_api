from datetime import date

from sqlalchemy import ForeignKey, String, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseDBModel
from app.schema.tour_booking import BookingStatus, PaymentStatus
from .setups import Country
from .tour import Tour


class TourBooking(BaseDBModel):
    __tablename__ = "tour_bookings"

    tour_id: Mapped[int] = mapped_column(ForeignKey("tours.id"), nullable=False)
    tour: Mapped["Tour"] = relationship("Tour")

    # customer info
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(50), nullable=False)
    country_id: Mapped[int] = mapped_column(ForeignKey("countries.id"), nullable=False)

    # booking details
    travel_date: Mapped[date] = mapped_column(nullable=True)
    number_of_people: Mapped[int] = mapped_column(Integer, default=1)

    # optional fields
    special_requests: Mapped[str | None] = mapped_column(Text)

    # status
    status: Mapped[str] = mapped_column(
        String(50), default=BookingStatus.PENDING.value, index=True
    )

    payment_status: Mapped[str] = mapped_column(
        String(50), default=PaymentStatus.NOT_REQUIRED.value
    )

    country: Mapped["Country"] = relationship(
        "Country",
        foreign_keys=[country_id],
    )

    def __repr__(self):
        return f"<TourBooking id={self.id} tour={self.tour_id}>"
