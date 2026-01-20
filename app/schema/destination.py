from typing import Optional, List, Dict

from pydantic import Field, BaseModel

from app.schema.hotel import Hotel
from app.schema.setups import City


class DestinationBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    image: Optional[str] = Field(None, max_length=500)
    highlights: Optional[List[str]] = None
    visitor_info: Optional[Dict] = None
    best_time: Optional[str] = Field(None, max_length=255)
    city_id: int
    slug: Optional[str] = None


class DestinationCreate(DestinationBase):
    hotel_ids: Optional[List[int]] = []


class DestinationUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    image: Optional[str] = Field(None, max_length=500)
    hotel_ids: Optional[List[int]] = None
    highlights: Optional[List[str]] = None
    visitor_info: Optional[Dict] = None
    best_time: Optional[str] = Field(None, max_length=255)
    city_id: Optional[int] = None


class Destination(DestinationBase):
    id: int
    is_active: bool
    hotels: List[Hotel]
    city: City

    class Config:
        from_attributes = True


class DestinationDetailed(Destination):
    hotels: List[Hotel] = []
