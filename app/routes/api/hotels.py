from typing import Optional, List

from fastapi import APIRouter, Depends, Query, status, Form, UploadFile, File
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repository.hotel import hotel_repository
from app.repository.setups import city_repository
from app.routes.deps import current_user
from app.schema import Pagination, HotelDetailed
from app.schema.hotel import Hotel, HotelCreate, HotelUpdate
from app.utils.utils import upload_image

router = APIRouter(prefix="/hotels", tags=["hotels"])


@router.get("/", response_model=Pagination[Hotel])
def list_hotels(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=100),
    city_id: Optional[int] = Query(None),
    country_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(None),
):
    filters = {}

    if city_id is not None:
        filters["city_id"] = city_id
    elif country_id:
        filters["country_id"] = country_id

    if is_active is not None:
        filters["is_active"] = is_active

    return hotel_repository.get_all_paginated(db, page=page, limit=limit, **filters)


@router.get("/{hotel_id}", response_model=HotelDetailed)
def get_hotel(hotel_id: int, db: Session = Depends(get_db)):
    return hotel_repository.get_object_or_404(db, id=hotel_id)


@router.post("/", response_model=HotelDetailed, status_code=status.HTTP_201_CREATED)
async def create_hotel(
    name: str = Form(...),
    price_per_night: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    rating: Optional[float] = Form(None),
    reviews_count: Optional[int] = Form(None),
    description: Optional[str] = Form(None),
    bedrooms: Optional[int] = Form(1),
    max_guests: Optional[int] = Form(2),
    amenities: Optional[str] = Form(None),
    files: List[UploadFile] = File(default=[]),
    db: Session = Depends(get_db),
    city_id: int = Form(None),
    user=Depends(current_user),
):
    urls = None
    if files:
        urls = [upload_image(i, is_public=True) for i in files]

    city = city_repository.get_object_or_404(db, id=city_id)
    hotel_data = HotelCreate(
        name=name,
        price_per_night=price_per_night,
        category=category,
        rating=rating,
        reviews_count=reviews_count,
        description=description,
        bedrooms=bedrooms,
        max_guests=max_guests,
        amenities=amenities.split(",") if amenities else None,
        images=urls,
        city_id=city.id,
        country_id=city.country_id,
    )

    return hotel_repository.create(db, hotel_data, audit_user_id=user.id)


@router.put("/{hotel_id}", response_model=HotelDetailed)
async def update_hotel(
    hotel_id: int,
    name: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    rating: Optional[float] = Form(None),
    reviews_count: Optional[int] = Form(None),
    price_per_night: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    bedrooms: Optional[int] = Form(None),
    max_guests: Optional[int] = Form(None),
    amenities: Optional[str] = Form(None),
    files: List[UploadFile] = File(default=[]),
    is_active: Optional[bool] = Form(None),
    db: Session = Depends(get_db),
    user=Depends(current_user),
    city_id: Optional[int] = Form(None),
):
    urls = None
    if files:
        urls = [upload_image(i, is_public=True) for i in files]

    country_id = None
    if city_id:
        country_id = city_repository.get_object_or_404(db, id=city_id).country_id

    hotel_update = HotelUpdate(
        name=name,
        category=category,
        rating=rating,
        reviews_count=reviews_count,
        price_per_night=price_per_night,
        description=description,
        bedrooms=bedrooms,
        max_guests=max_guests,
        amenities=amenities.split(",") if amenities else None,
        images=urls,
        city_id=city_id,
        country_id=country_id,
        is_active=is_active,
    )

    current = hotel_repository.get_object_or_404(db, id=hotel_id)

    return hotel_repository.update(
        db,
        current_item=current,
        item_in=hotel_update,
        audit_user_id=user.id,
    )


@router.delete("/{hotel_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_hotel(
    hotel_id: int,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    hotel_repository.delete(db, id=hotel_id, audit_user_id=user.id)
