from typing import Optional, List, Dict

from pydantic import BaseModel, Field

from app.schema.activity import Activity
from app.schema.destination import DestinationDetailed
from app.schema.hotel import Hotel
from app.schema.setups import City


class TourDayBase(BaseModel):
    day_number: int
    title: str
    description: Optional[str] = None
    meals: Optional[List[str]] = None
    hotel_id: Optional[int] = None
    tour_id: Optional[int] = None

    activity_ids: Optional[List[int]] = None


class TourDayCreate(TourDayBase):
    pass


class TourDayUpdate(BaseModel):
    day_number: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    meals: Optional[List[str]] = None
    hotel_id: Optional[int] = None
    tour_id: Optional[int] = None

    activity_ids: Optional[List[int]] = []


class TourDay(BaseModel):
    id: int
    day_number: int
    title: str
    description: Optional[str]
    meals: Optional[List[str]]
    hotel: Optional[Hotel]
    activities: List[Activity] = []
    activity_ids: List[int] = []

    class Config:
        from_attributes = True


class TourBase(BaseModel):
    title: str = Field(..., max_length=255)
    overview: Optional[str] = None
    duration: str
    price: float
    rating: float = 0.0
    reviews: int = 0
    max_participants: int = 20
    image_url: Optional[str] = None
    slug: Optional[str] = None
    highlights: Optional[List[str]] = None
    inclusions: Optional[List[str]] = None
    exclusions: Optional[List[str]] = None

    destination_id: int


class TourCreate(TourBase):
    itinerary: Optional[List[TourDayCreate]] = None


class TourUpdate(BaseModel):
    title: Optional[str] = None
    overview: Optional[str] = None
    duration: Optional[str] = None
    price: Optional[float] = None
    rating: Optional[float] = None
    reviews: Optional[int] = None
    max_participants: Optional[int] = None
    image_url: Optional[str] = None

    highlights: Optional[List[str]] = None
    inclusions: Optional[List[str]] = None
    exclusions: Optional[List[str]] = None

    destination_id: Optional[int] = None

    itinerary: Optional[List[TourDayUpdate]] = None


class _Destination(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    image: Optional[str] = Field(None, max_length=500)
    highlights: Optional[List[str]] = None
    visitor_info: Optional[Dict] = None
    best_time: Optional[str] = Field(None, max_length=255)
    city_id: int
    slug: Optional[str] = None
    city: City

    class Config:
        from_attributes = True


class Tour(TourBase):
    id: int
    destination: _Destination

    class Config:
        from_attributes = True


class TourDetailed(Tour):
    destination: Optional["DestinationDetailed"] = None
    itinerary: List[TourDay] = []

    class Config:
        from_attributes = True
