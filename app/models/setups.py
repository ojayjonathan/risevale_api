from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseDBModel

if TYPE_CHECKING:
    from .destination import Destination


class Country(BaseDBModel):
    __tablename__ = "countries"

    name: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )
    code: Mapped[str] = mapped_column(String(10), nullable=True, unique=True)

    cities: Mapped[list["City"]] = relationship("City", back_populates="country")

    def __repr__(self):
        return f"<Country(id={self.id}, name='{self.name}')>"


class City(BaseDBModel):
    __tablename__ = "cities"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    country_id: Mapped[int] = mapped_column(ForeignKey("countries.id"), nullable=False)

    country: Mapped["Country"] = relationship("Country", back_populates="cities")
    destinations: Mapped[list["Destination"]] = relationship(
        "Destination", back_populates="city"
    )

    def __repr__(self):
        return f"<City(id={self.id}, name='{self.name}')>"
