import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Generic, Optional, Type, TypeVar, List

from fastapi import HTTPException, status
from pydantic import BaseModel, ValidationError
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, Query

from app.models.base import BaseDBModel
from app.schema import SortModel, SortOrder
from app.utils.utils import calculate_total_pages

Model = TypeVar("Model", bound=BaseDBModel)
CreateSchema = TypeVar("CreateSchema", bound=BaseModel)
UpdateSchema = TypeVar("UpdateSchema", bound=BaseModel)


class AuditAction(str, Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    READ = "READ"


class SearchModel:
    def __init__(self, search_query: str, search_fields: List[str]):
        self.search_query = search_query
        self.search_fields = search_fields


def get_object_or_404(db: Session, model: Type[Model], **kwargs) -> Model:
    obj = db.query(model).filter_by(**kwargs).first()
    if obj:
        return obj

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={"message": f"{model.__name__} not found"},
    )


class BaseRepository(Generic[Model, CreateSchema, UpdateSchema]):
    def __init__(self, model: Type[Model]):
        self.model = model
        self.logger = logging.getLogger(f"{model.__name__}Repository")

    def log_audit(
        self,
        action: AuditAction | str,
        model_id: Optional = None,
        audit_user_id=None,
        details: Dict[str, Any] = None,
    ):
        self.logger.info(
            f"[AUDIT] {action} {self.model.__name__}(ID={model_id}) "
            f"User={audit_user_id} Details={details}"
        )

    def get(self, db: Session, id: int) -> Optional[Model]:
        return db.query(self.model).filter_by(id=id).first()

    def get_object_or_404(self, db: Session, **kwargs) -> Model:
        return get_object_or_404(db, self.model, **kwargs)

    def filter_by(self, db: Session, **kwargs) -> Query:
        return db.query(self.model).filter_by(**kwargs)

    def _filter_search_query(
        self,
        db: Session,
        sort: Optional[SortModel] = None,
        search: Optional[SearchModel] = None,
        **filters,
    ) -> Query:
        query = db.query(self.model)

        # Always exclude soft-deleted items
        conditions = []

        # Apply filters
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

    def get_all_paginated(
        self,
        db: Session,
        limit: Optional[int] = 20,
        page: Optional[int] = 1,
        search: Optional[SearchModel] = None,
        sort: Optional[SortModel] = None,
        **filters,
    ) -> dict:
        page = max(page or 1, 1)
        offset = (page - 1) * limit if limit else 0

        query = self._filter_search_query(db, sort=sort, search=search, **filters)
        count = query.count()

        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)

        return {
            "page": page,
            "data": query.all(),
            "count": count,
            "pages": calculate_total_pages(count, limit),
        }

    def get_all(
        self,
        db: Session,
        search: Optional[SearchModel] = None,
        sort: Optional[SortModel] = None,
        **filters,
    ) -> list:

        query = self._filter_search_query(db, sort=sort, search=search, **filters)
        return query.all()

    def create(
        self,
        db: Session,
        item: CreateSchema,
        audit_user_id: Optional[int] = None,
    ) -> Model:
        try:
            obj = self.model(**item.model_dump())

            if audit_user_id:
                obj.updated_by = audit_user_id

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
        item_in: UpdateSchema,
        audit_user_id: Optional[int] = None,
    ) -> Model:
        try:
            update_data = item_in.model_dump(exclude_unset=True)

            for field, value in update_data.items():
                if hasattr(current_item, field) and value is not None:
                    setattr(current_item, field, value)

            if audit_user_id:
                current_item.updated_by = audit_user_id

            db.commit()
            db.refresh(current_item)

            self.log_audit(
                AuditAction.UPDATE, current_item.id, audit_user_id, update_data
            )
            return current_item

        except Exception as e:
            db.rollback()
            self._handle_error(e)

    def delete(
        self,
        db: Session,
        obj: Optional[Model] = None,
        id: Optional[int] = None,
        audit_user_id: Optional[int] = None,
    ):
        if not obj:
            obj = self.get_object_or_404(db, id=id)

        try:
            db.delete(obj)
            db.commit()

            self.log_audit(AuditAction.DELETE, obj.id, audit_user_id)
            return obj

        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "message": "Cannot delete item because it is referenced by other records"
                },
            )

    def _handle_error(self, e: Exception):
        self.logger.error(str(e), exc_info=e)

        # Rethrow known errors
        if isinstance(e, (HTTPException, ValidationError)):
            raise e

        if isinstance(e, IntegrityError):
            msg = str(e.orig).lower()
            if "unique" in msg:
                message = "Duplicate entry — violates unique constraint"
            elif "foreign key" in msg:
                message = "Invalid reference — foreign key constraint failed"
            else:
                message = "Database integrity violation"

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": message, "error": str(e)},
            )

        # Generic server error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": "An unexpected error occurred", "error": str(e)},
        )
