from typing import TYPE_CHECKING

from sqlalchemy import String, Text, JSON, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseDBModel, metadata
from .hotel import Hotel

if TYPE_CHECKING:
    from .setups import City
    from .tour import Tour


class Destination(BaseDBModel):
    __tablename__ = "destinations"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    image: Mapped[str] = mapped_column(String(500), nullable=True)
    slug: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    highlights: Mapped[list[str]] = mapped_column(JSON, nullable=True)
    visitor_info: Mapped[dict] = mapped_column(JSON, nullable=True)
    best_time: Mapped[str] = mapped_column(String(255), nullable=True)
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id"), nullable=False)
    city: Mapped["City"] = relationship("City", back_populates="destinations")
    is_active: Mapped[bool] = mapped_column(default=True, index=True)

    tours: Mapped[list["Tour"]] = relationship("Tour", back_populates="destination")

    # Hotels relationship (many-to-many)
    hotels: Mapped[list["Hotel"]] = relationship(
        "Hotel", secondary="destination_hotels"
    )

    def __repr__(self):
        return f"<Destination(id={self.id}, name='{self.name}')>"


destination_hotels = Table(
    "destination_hotels",
    metadata,
    Column(
        "destination_id",
        ForeignKey("destinations.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column("hotel_id", ForeignKey("hotels.id", ondelete="CASCADE"), primary_key=True),
)
