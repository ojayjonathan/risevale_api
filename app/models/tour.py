from typing import TYPE_CHECKING

from sqlalchemy import (
    String,
    Integer,
    Float,
    Text,
    JSON,
    ForeignKey,
    Table,
    Column,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseDBModel, metadata

if TYPE_CHECKING:
    from .destination import Destination
    from .hotel import Hotel
    from .activity import Activity


# Many-to-many association table between TourDay and Activity
tour_day_activities = Table(
    "tour_day_activities",
    metadata,
    Column(
        "tour_day_id",
        ForeignKey("tour_days.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "activity_id",
        ForeignKey("activities.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Tour(BaseDBModel):
    __tablename__ = "tours"

    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    overview: Mapped[str] = mapped_column(Text, nullable=True)
    duration: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    rating: Mapped[float] = mapped_column(Float, default=0.0)
    reviews: Mapped[int] = mapped_column(Integer, default=0)
    max_participants: Mapped[int] = mapped_column(Integer, default=20)
    image_url: Mapped[str] = mapped_column(String(500), nullable=True)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    # JSON fields
    highlights: Mapped[list[str]] = mapped_column(JSON, nullable=True)
    inclusions: Mapped[list[str]] = mapped_column(JSON, nullable=True)
    exclusions: Mapped[list[str]] = mapped_column(JSON, nullable=True)

    # Foreign key to Destination
    destination_id: Mapped[int] = mapped_column(
        ForeignKey("destinations.id"), nullable=False
    )
    destination: Mapped["Destination"] = relationship(
        "Destination", back_populates="tours"
    )

    # Itinerary: list of TourDay objects (one-to-many)
    itinerary: Mapped[list["TourDay"]] = relationship(
        "TourDay",
        back_populates="tour",
        cascade="all, delete-orphan",
        order_by="TourDay.day_number",
    )

    is_active: Mapped[bool] = mapped_column(default=True, index=True)

    def __repr__(self):
        return f"<Tour(id={self.id}, title='{self.title}')>"

    def __int__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TourDay(BaseDBModel):
    __tablename__ = "tour_days"

    tour_id: Mapped[int] = mapped_column(
        ForeignKey("tours.id", ondelete="CASCADE"), nullable=False
    )
    day_number: Mapped[int] = mapped_column(Integer, nullable=False, index=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    # Optional nightly hotel
    hotel_id: Mapped[int | None] = mapped_column(
        ForeignKey("hotels.id", ondelete="CASCADE"), nullable=True
    )
    hotel: Mapped["Hotel"] = relationship("Hotel")

    # Activities (many-to-many)
    activities: Mapped[list["Activity"]] = relationship(
        "Activity",
        secondary=tour_day_activities,
        back_populates="tour_days",
    )

    # Meals stored as JSON
    meals: Mapped[list[str]] = mapped_column(JSON, default=[])

    # Back-reference to Tour
    tour: Mapped["Tour"] = relationship("Tour", back_populates="itinerary")

    @property
    def activity_ids(self):
        if not self.activities:
            return []
        return [a.id for a in self.activities]

    def __repr__(self):
        return f"<TourDay(tour_id={self.tour_id}, day={self.day_number})>"
