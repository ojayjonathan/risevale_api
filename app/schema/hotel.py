from typing import Optional, List

from pydantic import BaseModel, Field

from app.schema.setups import City


class HotelBase(BaseModel):
    name: str = Field(..., max_length=255)
    category: Optional[str] = Field(None, max_length=100)
    rating: Optional[float] = 0.0
    reviews_count: Optional[int] = 0
    price_per_night: Optional[str] = None
    description: Optional[str] = None
    bedrooms: Optional[int] = 1
    max_guests: Optional[int] = 2
    amenities: Optional[List[str]] = None
    images: Optional[List[str]] = None
    is_active: bool = True
    city_id: int
    country_id: int


class HotelCreate(HotelBase):
    pass


class HotelUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    category: Optional[str] = Field(None, max_length=100)
    rating: Optional[float] = None
    city_id: Optional[int] = None
    country_id: Optional[int] = None
    reviews_count: Optional[int] = None
    price_per_night: Optional[str] = None
    description: Optional[str] = None
    bedrooms: Optional[int] = None
    max_guests: Optional[int] = None
    images: Optional[List[str]] = None
    is_active: Optional[bool] = None


class Hotel(HotelBase):
    id: int
    amenities: Optional[List[str]] = Field([])
    city: City

    class Config:
        from_attributes = True


class HotelReview(BaseModel):
    id: int
    rating: float
    title: Optional[str] = None
    comment: Optional[str] = None
    user_id: Optional[int] = None

    class Config:
        from_attributes = True


class HotelDetailed(Hotel):
    reviews: List[HotelReview] = []

    class Config:
        from_attributes = True


class HotelReviewCreate(BaseModel):
    hotel_id: int
    user_id: Optional[int] = None
    rating: float = Field(..., ge=1, le=5)
    title: Optional[str] = None
    comment: Optional[str] = None
