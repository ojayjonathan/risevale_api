from typing import Optional

from pydantic import Field, BaseModel


class CountryBase(BaseModel):
    name: str = Field(..., max_length=255)
    code: Optional[str] = Field(None, max_length=10)


class CountryCreate(CountryBase):
    pass


class CountryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    code: Optional[str] = Field(None, max_length=10)


class Country(CountryBase):
    id: int

    class Config:
        from_attributes = True


class CityBase(BaseModel):
    name: str = Field(..., max_length=255)
    country_id: int


class CityCreate(CityBase):
    pass


class CityUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    country_id: Optional[int] = None


class City(CityBase):
    id: int
    country: Optional[Country] = None

    class Config:
        from_attributes = True
