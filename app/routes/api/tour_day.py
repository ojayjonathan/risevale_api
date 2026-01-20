from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repository.tour_day_repository import tour_day_repository
from app.routes.deps import current_user
from app.schema import TourDayCreate, TourDayUpdate, TourDay

router = APIRouter(prefix="/tour-days", tags=["tour-days"])


@router.post("/", response_model=TourDay, status_code=status.HTTP_201_CREATED)
def create_tour_day(
    day_in: TourDayCreate,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    return tour_day_repository.create(db, day_in, audit_user_id=user.id)


@router.get("/{day_id}", response_model=TourDay)
def get_tour_day(day_id: int, db: Session = Depends(get_db)):
    return tour_day_repository.get_object_or_404(db, id=day_id)


@router.put("/{day_id}", response_model=TourDay)
def update_tour_day(
    day_id: int,
    day_in: TourDayUpdate,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    current = tour_day_repository.get_object_or_404(db, id=day_id)

    return tour_day_repository.update(
        db, current_item=current, item_in=day_in, audit_user_id=user.id
    )


@router.delete("/{day_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tour_day(
    day_id: int,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    tour_day_repository.delete(db, id=day_id, audit_user_id=user.id)


@router.delete("/{day_id}/activities/{activity_id}", response_model=TourDay)
def remove_activity_from_day(
    day_id: int,
    activity_id: int,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    return tour_day_repository.remove_activity(
        db, tour_day_id=day_id, activity_id=activity_id, audit_user_id=user.id
    )
