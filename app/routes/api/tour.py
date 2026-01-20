from typing import Optional

from fastapi import APIRouter, Depends, status, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repository.tour import tour_repository
from app.routes.deps import current_user
from app.schema import TourCreate, TourUpdate, Pagination, Tour, TourDetailed
from app.utils.utils import upload_image

router = APIRouter(prefix="/tours", tags=["tours"])


@router.post("/", response_model=TourDetailed, status_code=status.HTTP_201_CREATED)
def create_tour(
    tour_in: TourCreate,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    return tour_repository.create(db, tour_in, audit_user_id=user.id)


@router.get("/", response_model=Pagination[Tour])
def list_tours(
    page: int = 1,
    limit: int = 100,
    destination_id: Optional[int] = None,
    city_id: Optional[int] = None,
    country_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
):

    filters = {}
    if destination_id:
        filters["destination_id"] = destination_id
    if country_id:
        filters["country_id"] = country_id
    if city_id:
        filters["city_id"] = city_id
    if is_active is not None:
        filters["is_active"] = is_active

    return tour_repository.get_all_paginated(db, page=page, limit=limit, **filters)


@router.get("/{slug}", response_model=TourDetailed)
def get_tour(
    slug: str,
    db: Session = Depends(get_db),
):
    return tour_repository.get_object_or_404(db, slug=slug)


@router.put("/{tour_id}", response_model=TourDetailed)
def update_tour(
    tour_id: int,
    tour_in: TourUpdate,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    current = tour_repository.get_object_or_404(db, id=tour_id)

    return tour_repository.update(
        db,
        current_item=current,
        item_in=tour_in,
        audit_user_id=user.id,
    )


@router.post("/upload/file", response_model=str)
def upload_file(file: UploadFile, _user=Depends(current_user)):
    return upload_image(file)


@router.delete("/{tour_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tour(
    tour_id: int,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    tour_repository.delete(db, id=tour_id, audit_user_id=user.id)
