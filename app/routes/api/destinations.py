import json
from typing import Optional

from fastapi import APIRouter, Depends, Query, status, Form, UploadFile, File
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repository.destination import destination_repository
from app.routes.deps import current_user
from app.schema import Pagination
from app.schema.destination import (
    DestinationCreate,
    DestinationUpdate,
    Destination,
    DestinationDetailed,
)
from app.utils.utils import upload_image

router = APIRouter(prefix="/destinations", tags=["destinations"])


@router.get("/", response_model=Pagination[Destination])
def list_destinations(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=100),
    city_id: Optional[int] = None,
    country_id: Optional[int] = None,
):
    filters = {}
    if city_id:
        filters["city_id"] = city_id

    if country_id:
        filters["country_id"] = country_id

    return destination_repository.get_all_paginated(
        db, page=page, limit=limit, **filters
    )


@router.get("/{slug}", response_model=DestinationDetailed)
def get_destination(slug: str, db: Session = Depends(get_db)):
    return destination_repository.get_object_or_404(db, slug=slug)


@router.post(
    "/", response_model=DestinationDetailed, status_code=status.HTTP_201_CREATED
)
def create_destination(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    city_id: int = Form(...),
    best_time: Optional[str] = Form(None),
    highlights: Optional[str] = Form(None),
    visitor_info: Optional[str] = Form(None),
    image: Optional[UploadFile] = Form(None),
    hotel_ids: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    user=Depends(current_user),
):

    data = DestinationCreate(
        name=name,
        description=description,
        city_id=city_id,
        best_time=best_time,
        highlights=highlights.split(",") if highlights else None,
        visitor_info=json.loads(visitor_info) if visitor_info else None,
        hotel_ids=hotel_ids.split(",") if hotel_ids else None,
        image=upload_image(image),
    )

    return destination_repository.create(db, data, audit_user_id=user.id)


@router.put("/{destination_id}", response_model=DestinationDetailed)
def update_destination(
    destination_id: int,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    city_id: Optional[int] = Form(None),
    best_time: Optional[str] = Form(None),
    highlights: Optional[str] = Form(None),
    visitor_info: Optional[str] = Form(None),
    hotel_ids: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    user=Depends(current_user),
):

    data = DestinationUpdate(
        name=name,
        description=description,
        city_id=city_id,
        best_time=best_time,
        highlights=highlights.split(",") if highlights else None,
        visitor_info=json.loads(visitor_info) if visitor_info else None,
        hotel_ids=hotel_ids.split(",") if hotel_ids else None,
        image=upload_image(image),
    )

    current = destination_repository.get_object_or_404(db, id=destination_id)

    return destination_repository.update(
        db, current_item=current, item_in=data, audit_user_id=user.id
    )


@router.delete("/{destination_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_destination(
    destination_id: int, db: Session = Depends(get_db), user=Depends(current_user)
):
    return destination_repository.delete(db, id=destination_id, audit_user_id=user.id)


@router.delete("/{destination_id}/{hotel_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_destination_hotel(
    destination_id: int,
    hotel_id: int,
    db: Session = Depends(get_db),
    _user=Depends(current_user),
):
    return destination_repository.delete_hotel(db, id=destination_id, hotel_id=hotel_id)
