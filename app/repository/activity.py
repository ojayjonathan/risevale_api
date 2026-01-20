from app.models.activity import Activity
from app.repository.base import BaseRepository
from app.schema.activity import ActivityCreate, ActivityUpdate


class ActivityRepository(BaseRepository[Activity, ActivityCreate, ActivityUpdate]):

    def __init__(self):
        super().__init__(Activity)


activity_repository = ActivityRepository()

__all__ = ["ActivityRepository", "activity_repository"]
