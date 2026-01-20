from datetime import datetime
from operator import or_
from typing import Optional

from sqlalchemy.orm import Session, Query

from app import models
from app.models.tour import Tour
from app.repository.base import BaseRepository, SearchModel
from app.repository.tour_day_repository import tour_day_repository
from app.schema import TourCreate, TourUpdate, SortModel, SortOrder
from app.utils.utils import slugify


class TourRepository(BaseRepository[Tour, TourCreate, TourUpdate]):

    def __init__(self):
        super().__init__(Tour)

    def create(
        self, db: Session, item: TourCreate, audit_user_id: Optional[int] = None
    ) -> Tour:
        try:
            db_tour = Tour(
                title=item.title,
                overview=item.overview,
                duration=item.duration,
                price=item.price,
                rating=item.rating,
                reviews=item.reviews,
                max_participants=item.max_participants,
                image_url=item.image_url,
                highlights=item.highlights,
                inclusions=item.inclusions,
                exclusions=item.exclusions,
                destination_id=item.destination_id,
                slug=slugify(item.title),
            )

            db.add(db_tour)
            db.flush()

            # Create itinerary
            if item.itinerary:
                for day in item.itinerary:
                    tour_day = models.TourDay(
                        tour_id=db_tour.id,
                        day_number=day.day_number,
                        title=day.title,
                        description=day.description,
                        meals=day.meals,
                        hotel_id=day.hotel_id,
                    )

                    if day.activity_ids:
                        tour_day.activities = (
                            db.query(models.Activity)
                            .filter(models.Activity.id.in_(day.activity_ids))
                            .all()
                        )

                    db.add(tour_day)

            db.commit()
            db.refresh(db_tour)
            return db_tour

        except Exception as e:
            self.logger(f"Error Creating tour {e}", exc_info=e)
            self._handle_error(e)

    def update(
        self,
        db: Session,
        current_item: Tour,
        item_in: TourUpdate,
        audit_user_id: Optional[int] = None,
    ) -> Tour:

        try:
            update_data = item_in.model_dump(exclude_unset=True, exclude={"itinerary"})
            for field, value in update_data.items():
                if hasattr(current_item, field) and value is not None:
                    print(current_item, field, value)
                    setattr(current_item, field, value)

            if audit_user_id:
                current_item.updated_by = audit_user_id

            if item_in.itinerary:
                for day_in in item_in.itinerary:
                    existing_days = {d.id: d for d in current_item.itinerary}
                    day_in.tour_id = current_item.id
                    if getattr(day_in, "id", None):
                        db_day = existing_days.get(day_in.id)
                        updated_day = tour_day_repository.update(
                            db=db,
                            current_item=db_day,
                            item_in=day_in,
                            audit_user_id=audit_user_id,
                        )
                    else:
                        new_day = tour_day_repository.create(
                            db=db,
                            item=day_in,
                            audit_user_id=audit_user_id,
                        )

            db.commit()
            db.refresh(current_item)

            return current_item
        except Exception as e:
            self.logger.error(f"Error Creating tour {e}", exc_info=e)
            self._handle_error(e)

        return current_item

    def _filter_search_query(
        self,
        db: Session,
        sort: Optional[SortModel] = None,
        search: Optional[SearchModel] = None,
        **filters,
    ) -> Query:
        query = db.query(models.Tour)

        conditions = []

        if "city_id" in filters:
            query = query.join(
                models.Destination, models.Destination.id == models.Tour.destination_id
            ).filter(models.Destination.city_id == filters["city_id"])
            filters.pop("city_id")

        elif "country_id" in filters:
            query = (
                query.join(
                    models.Destination,
                    models.Destination.id == models.Tour.destination_id,
                )
                .join(models.City, models.City.id == models.Destination.city_id)
                .filter(models.City.country_id == filters["country_id"])
            )
            filters.pop("country_id")

        for k, v in filters.items():
            if hasattr(self.model, k):
                column = getattr(self.model, k)
                if isinstance(v, list):
                    conditions.append(column.in_(v))
                else:
                    conditions.append(column == v)

            elif k == "date_from":
                conditions.append(self.model.created_at >= v)

            elif k == "date_to":
                conditions.append(
                    self.model.created_at <= datetime(v.year, v.month, v.day, 23, 59)
                )

        # Apply search query
        if search and search.search_query:
            search_filters = []
            for field in search.search_fields:
                if hasattr(self.model, field):
                    col = getattr(self.model, field)
                    search_filters.append(col.ilike(f"%{search.search_query}%"))
            if search_filters:
                conditions.append(or_(*search_filters))

        query = query.filter(*conditions)

        # Apply sorting
        if sort and hasattr(self.model, sort.sort):
            column = getattr(self.model, sort.sort)
            query = query.order_by(
                column.desc() if sort.direction == SortOrder.desc else column.asc()
            )
        else:
            query = query.order_by(self.model.id.desc())

        return query


# Create singleton instance
tour_repository = TourRepository()

__all__ = ["TourRepository", "tour_repository"]
