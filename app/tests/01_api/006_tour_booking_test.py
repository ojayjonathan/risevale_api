from app import models
from app.schema.tour_booking import PaymentStatus, BookingStatus
from app.tests.conftest import get_test_db


def test_create_booking(client, get_test_db):
    payload = {
        "full_name": "John Doe",
        "phone": "0712345678",
        "email": "john@example.com",
        "tour_id": 1,
        "number_of_people": 2,
        "preferred_date": "2025-01-16T10:00:00",
        "country_id": get_test_db.query(models.Country).first().id,
    }

    response = client.post("/bookings/", json=payload)
    data = response.json()

    assert response.status_code == 201
    assert data["payment_status"] == PaymentStatus.PENDING
    assert data["status"] == BookingStatus.PENDING
    assert data["full_name"] == "John Doe"


def test_list_bookings(client, auth_headers):
    response = client.get("/bookings/", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)


def test_update_booking(client, auth_headers):
    payload = {"payment_status": "PAID", "status": "CONFIRMED"}

    response = client.put("/bookings/1", json=payload, headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["payment_status"] == "PAID"
    assert data["status"] == "CONFIRMED"
