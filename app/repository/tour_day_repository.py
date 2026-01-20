from typing import Optional

from sqlalchemy.orm import Session

from app import models
from app.models.tour import TourDay
from app.repository.base import BaseRepository, get_object_or_404
from app.schema import TourDayUpdate, TourDayCreate


class TourDayRepository(BaseRepository[TourDay, TourDayCreate, TourDayUpdate]):

    def __init__(self):
        super().__init__(TourDay)

    def create(
        self,
        db: Session,
        item: TourDayCreate,
        audit_user_id: Optional[int] = None,
    ) -> TourDay:
        try:
            # Prevent duplicate days
            existing: TourDay | None = (
                db.query(models.TourDay)
                .filter(
                    models.TourDay.tour_id == item.tour_id,
                    models.TourDay.day_number == item.day_number,
                )
                .first()
            )
            if existing:
                return self.update(
                    db=db,
                    current_item=existing,
                    item_in=TourDayUpdate(**item.model_dump()),
                    audit_user_id=audit_user_id,
                )

            # Create new
            db_item = models.TourDay(
                tour_id=item.tour_id,
                day_number=item.day_number,
                title=item.title,
                description=item.description,
                meals=item.meals,
                hotel_id=item.hotel_id,
            )

            # Attach activities
            if item.activity_ids:
                db_item.activities = (
                    db.query(models.Activity)
                    .filter(models.Activity.id.in_(item.activity_ids))
                    .all()
                )

            db.add(db_item)
            db.commit()
            db.refresh(db_item)

            return db_item

        except Exception as e:
            self.logger.error(f"Error creating tour day: {e}", exc_info=e)
            self._handle_error(e)

    def remove_activity(
        self,
        db: Session,
        tour_day_id: int,
        activity_id: int,
        audit_user_id: Optional[int] = None,
    ):
        try:
            tour_day = self.get_object_or_404(db, id=tour_day_id)

            if not tour_day:
                raise ValueError(f"TourDay {tour_day_id} not found")

            activity = get_object_or_404(model=models.Activity, db=db, id=activity_id)

            if activity in tour_day.activities:
                tour_day.activities.remove(activity)

            if audit_user_id:
                tour_day.updated_by = audit_user_id

            db.commit()
            db.refresh(tour_day)

            return tour_day

        except Exception as e:
            self.logger.error(f"Error removing activity: {e}", exc_info=e)
            self._handle_error(e)

    def update(
        self,
        db: Session,
        current_item: TourDay,
        item_in: TourDayUpdate,
        audit_user_id: Optional[int] = None,
    ) -> TourDay:
        try:
            update_data = item_in.model_dump(exclude_unset=True)

            # Update fields
            for field, value in update_data.items():
                if field not in ("activity_ids",):
                    if hasattr(current_item, field):
                        setattr(current_item, field, value)

            # Update activities
            if item_in.activity_ids is not None:
                current_item.activities = (
                    db.query(models.Activity)
                    .filter(models.Activity.id.in_(item_in.activity_ids))
                    .all()
                )

            if audit_user_id:
                current_item.updated_by = audit_user_id

            db.commit()
            db.refresh(current_item)

            return current_item

        except Exception as e:
            self.logger(f"Error updating tour day: {e}", exc_info=e)
            self._handle_error(e)

        return current_item


# Singleton instance
tour_day_repository = TourDayRepository()

__all__ = ["TourDayRepository", "tour_day_repository"]
