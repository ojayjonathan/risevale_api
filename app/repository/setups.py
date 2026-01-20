from app.models.setups import Country, City
from app.repository.base import BaseRepository
from app.schema.setups import CountryCreate, CountryUpdate, CityCreate, CityUpdate


class CountryRepository(BaseRepository[Country, CountryCreate, CountryUpdate]):

    def __init__(self):
        super().__init__(Country)


country_repository = CountryRepository()


class CityRepository(BaseRepository[City, CityCreate, CityUpdate]):

    def __init__(self):
        super().__init__(City)


city_repository = CityRepository()

__all__ = [
    "CountryRepository",
    "country_repository",
    "city_repository",
    "CityRepository",
]
