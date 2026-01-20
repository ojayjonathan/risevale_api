from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class BaseDBModel(DeclarativeBase):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )
    updated_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    deleted_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, self.__class__):
            return False
        if not hasattr(other, "id"):
            return False
        return self.id == other.id


metadata = BaseDBModel.metadata
