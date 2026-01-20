from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, JSON
from sqlalchemy import String, Integer, Float, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseDBModel

if TYPE_CHECKING:
    from .setups import City


class Hotel(BaseDBModel):
    __tablename__ = "hotels"
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    category: Mapped[str] = mapped_column(String(100), nullable=True, index=True)
    rating: Mapped[float] = mapped_column(Float, default=0.0)
    reviews_count: Mapped[int] = mapped_column(Integer, default=0, nullable=True)
    price_per_night: Mapped[str] = mapped_column(String, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    bedrooms: Mapped[int] = mapped_column(Integer, default=1, nullable=True)
    max_guests: Mapped[int] = mapped_column(Integer, default=2, nullable=True)
    amenities: Mapped[list[str]] = mapped_column(JSON, nullable=True)
    images: Mapped[list[str]] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(
        default=True, index=True, server_default="True"
    )
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id"), nullable=False)
    city: Mapped["City"] = relationship("City", foreign_keys=city_id)
    country_id: Mapped[int] = mapped_column(ForeignKey("countries.id"), nullable=False)
    country: Mapped["City"] = relationship("Country", foreign_keys=country_id)

    # relationships
    reviews: Mapped[list["HotelReview"]] = relationship(
        "HotelReview", back_populates="hotel"
    )

    def __repr__(self):
        return f"<Hotel(id={self.id}, name='{self.name}')>"


class HotelReview(BaseDBModel):
    __tablename__ = "hotel_reviews"

    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id"), nullable=False)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    rating: Mapped[float] = mapped_column(Float, nullable=False)  # 1–5
    title: Mapped[str] = mapped_column(Text, nullable=True)
    comment: Mapped[str] = mapped_column(Text, nullable=True)

    hotel: Mapped["Hotel"] = relationship("Hotel", back_populates="reviews")

    def __repr__(self):
        return f"<HotelReview(id={self.id}, hotel_id={self.hotel_id}, rating={self.rating})>"
