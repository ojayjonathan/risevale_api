from enum import Enum
from typing import Dict, TypeVar, Generic, List, Optional, Annotated, Any

from pydantic import BaseModel, Field

from .activity import Activity, ActivityCreate, ActivityUpdate
from .auth import AccessToken, PasswordResetComplete, PasswordResetInit, AccessTokenData
from .destination import Destination, DestinationCreate, DestinationUpdate
from .hotel import (
    Hotel,
    HotelCreate,
    HotelDetailed,
    HotelReview,
    HotelReviewCreate,
    HotelUpdate,
)
from .setups import (
    City,
    CityCreate,
    Country,
    CountryCreate,
    CountryUpdate,
    CityUpdate,
    CountryBase,
    CityBase,
)
from .tour import (
    Tour,
    TourCreate,
    TourDay,
    TourDayCreate,
    TourDayUpdate,
    TourDetailed,
    TourUpdate,
)
from .tour_booking import TourBooking, TourBookingCreate


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


class SortModel(BaseModel):
    sort: str = Field(default="created_at")
    direction: SortOrder = Field(default=SortOrder.desc)


class MessageResponse(BaseModel):
    message: str
    details: Annotated[
        Dict[str, Any], Field(default={}, description="Details of the message")
    ]


class ErrorResponse(BaseModel):
    message: str
    detail: Annotated[
        Dict[str, Dict[str, str]], Field(default={}, description="Details of the error")
    ]


DataSchema = TypeVar("DataSchema", bound=BaseModel)


class Pagination(BaseModel, Generic[DataSchema]):
    data: List[DataSchema]
    page: int
    pages: int
    count: Optional[int] = None

    class Config:
        from_attributes = True
