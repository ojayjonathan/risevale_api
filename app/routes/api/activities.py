from typing import Optional

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repository.activity import activity_repository
from app.routes.deps import current_user
from app.schema import Pagination
from app.schema.activity import ActivityCreate, ActivityUpdate, Activity

router = APIRouter(prefix="/activities", tags=["activities"])


@router.get("/", response_model=Pagination[Activity])
def list_activities(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=100),
    activity_type: Optional[str] = Query(None, pattern="^(included|optional)$"),
):
    filters = {"is_active": True}

    if activity_type:
        filters["type"] = activity_type

    return activity_repository.get_all_paginated(db, limit=limit, page=page, **filters)


@router.get("/{activity_id}", response_model=Activity)
def get_activity(activity_id: int, db: Session = Depends(get_db)):
    return activity_repository.get_object_or_404(db, id=activity_id)


@router.post("/", response_model=Activity, status_code=status.HTTP_201_CREATED)
def create_activity(
    activity_in: ActivityCreate,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    return activity_repository.create(db, activity_in, audit_user_id=user.id)


@router.put("/{activity_id}", response_model=Activity)
def update_activity(
    activity_id: int,
    activity_in: ActivityUpdate,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    return activity_repository.update(
        db,
        current_item=activity_repository.get_object_or_404(db, id=activity_id),
        item_in=activity_in,
        audit_user_id=user.id,
    )


@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    audit_user_id: Optional[int] = None,
):
    return activity_repository.delete(db, id=activity_id, audit_user_id=audit_user_id)
