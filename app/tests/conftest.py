from app.core.config import Environment, get_settings, Settings
from app.models.base import BaseDBModel

if get_settings().ENVIRONMENT == Environment.local:
    get_settings().REDIS_HOST = "localhost"

get_settings().ENVIRONMENT = Environment.test


# content of conftest.py
from typing import Dict
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.core.security import hash_password
from app.models import User, City, Country
from app.routes.deps import get_db
from app.main import app
from app.tests.db_session import TestingSessionLocal, engine
from sqlalchemy.exc import SQLAlchemyError
from psycopg2 import errors as psycopg2_errors

from app.prepare_tests import setup

setup()

BaseDBModel.metadata.create_all(bind=engine)


def get_db_override():
    db = TestingSessionLocal()
    try:
        yield db
    except (SQLAlchemyError, psycopg2_errors.DatabaseError):
        db.rollback()
        raise
    finally:
        db.close()


app.dependency_overrides[get_db] = get_db_override


@pytest.fixture(scope="module")
def client():
    with TestClient(app, headers={}) as c:
        yield c


@pytest.fixture(scope="module")
def settings():
    yield get_settings()


@pytest.fixture(scope="session")
def get_test_db():
    db = None
    try:
        db = TestingSessionLocal()
        yield db

    except Exception:
        db.rollback()
        raise
    finally:
        ...


@pytest.fixture(scope="module")
def auth_headers(settings: Settings, get_user: User, client: TestClient) -> Dict:
    response = client.post(
        "/auth/login/",
        json={
            "password": settings.TEST_USER_PASSWORD,
            "email": settings.TEST_USER_EMAIL,
        },
    )

    return {
        "Authorization": f"Bearer {response.json()['access_token']}",
    }


@pytest.fixture(scope="module")
def get_user(get_test_db: Session, settings: Settings = get_settings()):
    test_user = (
        get_test_db.query(User).filter_by(email=settings.TEST_USER_EMAIL).first()
    )
    if not test_user:
        # create test user
        test_user = User(
            full_name="John Doe",
            password=hash_password(settings.TEST_USER_PASSWORD),
            email=settings.TEST_USER_EMAIL,
        )
        get_test_db.add(test_user)

        get_test_db.commit()
    yield test_user


@pytest.fixture
def get_country(get_test_db, name="Kenya", code="KE"):
    country = get_test_db.query(Country).filter(Country.name == name).first()
    if country:
        return country

    country = Country(name=name, code=code)
    get_test_db.add(country)
    get_test_db.commit()
    get_test_db.refresh(country)
    return country


@pytest.fixture
def get_city(get_test_db, get_country, name="Nairobi"):

    city = (
        get_test_db.query(City)
        .filter(City.name == name, City.country_id == get_country.id)
        .first()
    )
    if city:
        return city

    city = City(name=name, country_id=get_country.id)
    get_test_db.add(city)
    get_test_db.commit()
    get_test_db.refresh(city)
    return city
