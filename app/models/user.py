from typing import Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseDBModel


class User(BaseDBModel):
    __tablename__ = "users"

    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    password: Mapped[str] = mapped_column(String(150), nullable=False)
