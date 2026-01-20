from typing import TYPE_CHECKING

from sqlalchemy import String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseDBModel
from . import TourDay

if TYPE_CHECKING:
    pass


class Activity(BaseDBModel):
    __tablename__ = "activities"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    image: Mapped[str] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    tour_days: Mapped[list["TourDay"]] = relationship(
        "TourDay", secondary="tour_day_activities", back_populates="activities"
    )

    def __repr__(self):
        return f"<Activity(id={self.id}, title='{self.title}')>"
