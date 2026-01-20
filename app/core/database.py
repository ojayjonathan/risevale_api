import logging
from typing import Generator

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
settings = get_settings()

engine_kwargs = {
    "pool_size": 20,
    "max_overflow": 30,
    "echo": settings.ENVIRONMENT in ["local", "test"],
    "pool_reset_on_return": "rollback",
    "pool_recycle": 3600,
}

# Add connection args only for non-SQLite databases
if "postgresql" in str(settings.DATABASE_URI):
    engine_kwargs["connect_args"] = {
        "connect_timeout": 10,
        "application_name": "RISEVALE_TOUR_API",
        "options": "-c timezone=Africa/Nairobi",
    }

engine = create_engine(settings.DATABASE_URI, **engine_kwargs)
logger.info(f"Database engine created for environment: {settings.ENVIRONMENT}")

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=Session,
)


def get_db() -> Generator[Session, None, None]:
    db: Session = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("Database error occurred", exc_info=e)
        raise HTTPException(
            status_code=500,
            detail="A database error occurred. Please try again later.",
        )
    finally:
        db.close()


__all__ = ["engine", "SessionLocal", "get_db"]
