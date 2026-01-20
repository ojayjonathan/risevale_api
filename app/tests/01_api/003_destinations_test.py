from fastapi.testclient import TestClient

from app.main import app
from app.models import Hotel
from app.tests.conftest import get_test_db

client = TestClient(app)


# Helper to create a hotel
def create_hotel(get_test_db):
    hotel = Hotel(
        name="Test Hotel",
        price_per_night="100.0 Ksh",
        category="budget",
        rating=4.5,
        reviews_count=10,
        amenities=["wifi", "breakfast"],
        images=["img1.jpg"],
        bedrooms=1,
        max_guests=2,
        city_id=1,
        country_id=1,
        description="A simple test hotel",
        is_active=True,
    )

    get_test_db.add(hotel)
    get_test_db.commit()
    get_test_db.refresh(hotel)

    return hotel.id


# Helper to create a destination
def create_destination(hotel_id, auth_headers):
    payload = {
        "name": "Nairobi National Park",
        "description": "Wildlife near the city",
        "image": "nairobi_park.jpg",
        "highlights": ["lions", "buffalo"],
        "visitor_info": {"hours": "6am - 6pm"},
        "best_time": "June - October",
        "city_id": 1,
        "hotel_ids": [hotel_id],
    }
    res = client.post("/destinations/", json=payload, headers=auth_headers)
    assert res.status_code == 201
    return res.json()


# ------------------------------------------------------------
# TESTS
# ------------------------------------------------------------


def test_list_empty(get_test_db):
    res = client.get("/destinations/?page=1&limit=10")
    assert res.status_code == 200
    assert res.json()["data"] == []


def test_create_destination(get_test_db, auth_headers):
    hotel_id = create_hotel(get_test_db)
    data = create_destination(hotel_id, auth_headers)

    assert data["name"] == "Nairobi National Park"


def test_list_destinations(
    get_test_db,
):
    hotel_id = create_hotel(get_test_db)

    res = client.get("/destinations/")
    assert res.status_code == 200
    assert len(res.json()["data"]) >= 1


def test_get_destination(get_test_db, auth_headers):
    hotel_id = create_hotel(get_test_db)
    created = create_destination(hotel_id, auth_headers)

    res = client.get(f"/destinations/{created['slug']}")
    assert res.status_code == 200
    assert res.json()["id"] == created["id"]


def test_update_destination(get_test_db, auth_headers):
    hotel_id = create_hotel(get_test_db)
    created = create_destination(hotel_id, auth_headers)

    update_payload = {
        "name": "Updated Park",
        "description": "Updated desc",
        "image": None,
        "highlights": ["updated"],
        "visitor_info": {},
        "best_time": "All year",
        "city_id": 1,
        "hotel_ids": [hotel_id],
    }

    res = client.put(
        f"/destinations/{created['id']}", json=update_payload, headers=auth_headers
    )
    assert res.status_code == 200
    assert res.json()["name"] == "Updated Park"


def test_delete_destination(get_test_db, auth_headers):
    hotel_id = create_hotel(get_test_db)
    created = create_destination(hotel_id, auth_headers)

    res = client.delete(f"/destinations/{created['id']}", headers=auth_headers)
    assert res.status_code == 204

    # Ensure deleted
    res2 = client.get(f"/destinations/{created['id']}")
    assert res2.status_code == 404
