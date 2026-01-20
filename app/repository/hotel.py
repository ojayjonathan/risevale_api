from app.models.hotel import Hotel
from app.repository.base import BaseRepository
from app.schema.hotel import HotelCreate, HotelUpdate


class HotelRepository(BaseRepository[Hotel, HotelCreate, HotelUpdate]):

    def __init__(self):
        super().__init__(Hotel)


hotel_repository = HotelRepository()

__all__ = ["HotelRepository", "hotel_repository"]
