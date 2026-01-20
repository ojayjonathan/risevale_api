from typing import Optional

from pydantic import Field, BaseModel


class ActivityBase(BaseModel):
    title: str = Field(..., max_length=255)
    type: str = Field(..., max_length=100)
    description: Optional[str] = None
    image: Optional[str] = Field(None, max_length=500)
    is_active: bool = True


class ActivityCreate(ActivityBase):
    pass


class ActivityUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    type: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    image: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None


class Activity(ActivityBase):
    id: int

    class Config:
        from_attributes = True
