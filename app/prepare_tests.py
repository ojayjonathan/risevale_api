import logging
import os

from sqlalchemy.orm import sessionmaker

from app.models.base import BaseDBModel
from app.tests.db_session import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup():
    if os.path.exists("test.db"):
        os.remove("test.db")

    sessionmaker(autocommit=False, autoflush=False, bind=engine)
    BaseDBModel.metadata.create_all(bind=engine)

    logger.info("Sample data loaded successfully")
