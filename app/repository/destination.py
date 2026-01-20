from typing import Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session, Query

from app import models
from app.models.destination import Destination
from app.repository.base import BaseRepository, Model, AuditAction, SearchModel
from app.schema import SortOrder, SortModel
from app.schema.destination import DestinationCreate, DestinationUpdate
from app.utils.utils import slugify


class DestinationRepository(
    BaseRepository[Destination, DestinationCreate, DestinationUpdate]
):

    def __init__(self):
        super().__init__(Destination)

    def create(
        self, db: Session, item: DestinationCreate, audit_user_id: Optional[int] = None
    ) -> Destination:
        try:
            item.slug = slugify(item.name)
            obj = models.Destination(**item.model_dump(exclude={"hotel_ids"}))

            if audit_user_id:
                obj.updated_by = audit_user_id

            if item.hotel_ids:
                obj.hotels = (
                    db.query(models.Hotel)
                    .filter(models.Hotel.id.in_(item.hotel_ids))
                    .all()
                )

            db.add(obj)
            db.commit()
            db.refresh(obj)

            self.log_audit(AuditAction.CREATE, obj.id, audit_user_id, item.model_dump())
            return obj

        except Exception as e:
            db.rollback()
            self._handle_error(e)

    def update(
        self,
        db: Session,
        current_item: Model,
        item_in: DestinationUpdate,
        audit_user_id: Optional[int] = None,
    ) -> Destination:
        try:
            update_data = item_in.model_dump(exclude_unset=True)

            for field, value in update_data.items():
                if hasattr(current_item, field) and value is not None:
                    setattr(current_item, field, value)

            if audit_user_id:
                current_item.updated_by = audit_user_id

            if item_in.hotel_ids:
                current_item.hotels = (
                    db.query(models.Hotel)
                    .filter(models.Hotel.id.in_(item_in.hotel_ids))
                    .all()
                )

            db.commit()
            db.refresh(current_item)

            self.log_audit(
                AuditAction.UPDATE, current_item.id, audit_user_id, update_data
            )
            return current_item

        except Exception as e:
            db.rollback()
            self._handle_error(e)

    def delete_hotel(self, db: Session, destination_id, hotel_id):
        try:
            item = db.query(models.destination_hotels).filter_by(
                destination_id=destination_id, hotel_id=hotel_id
            )
            db.delete(item)
            db.commit()
        except Exception as e:
            db.rollback()
            self._handle_error(e)

    def _filter_search_query(
        self,
        db: Session,
        sort: Optional[SortModel] = None,
        search: Optional[SearchModel] = None,
        **filters,
    ) -> Query:
        query = db.query(models.Destination)

        conditions = []

        if "country_id" in filters and not "city_id" in filters:
            query = query.join(
                models.City, models.City.id == models.Destination.city_id
            ).filter(models.City.country_id == filters["country_id"])
            filters.pop("country_id")

        for k, v in filters.items():
            if hasattr(self.model, k):
                column = getattr(self.model, k)
                if isinstance(v, list):
                    conditions.append(column.in_(v))
                else:
                    conditions.append(column == v)

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


destination_repository = DestinationRepository()

__all__ = ["DestinationRepository", "destination_repository"]
