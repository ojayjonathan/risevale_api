from sqlalchemy import String, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseDBModel


class Blog(BaseDBModel):
    __tablename__ = "blogs"

    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    excerpt: Mapped[str] = mapped_column(Text, nullable=True)
    image: Mapped[str] = mapped_column(String(500), nullable=True)
    author: Mapped[str] = mapped_column(String(255), nullable=False)
    tags: Mapped[str] = mapped_column(Text, nullable=True)
    views: Mapped[int] = mapped_column(Integer, default=0)
    is_published: Mapped[bool] = mapped_column(default=False, index=True)

    def __repr__(self):
        return f"<Blog(id={self.id}, title='{self.title}', slug='{self.slug}')>"
