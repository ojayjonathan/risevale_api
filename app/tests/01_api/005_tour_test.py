from app.models import Hotel, Destination
from app.models.activity import Activity
from app.models.tour import Tour, TourDay
from app.utils.utils import slugify


def test_create_tour(get_test_db, client, auth_headers):

    destination = get_test_db.query(Destination).first()
    activities = get_test_db.query(Activity).all()
    hotel = get_test_db.query(Hotel).first()

    payload = {
        "title": "Safari Adventure",
        "overview": "A great safari experience.",
        "duration": "5 days",
        "price": 500.0,
        "rating": 4.7,
        "reviews": 200,
        "max_participants": 10,
        "image_url": "img.jpg",
        "highlights": ["wildlife", "camping"],
        "inclusions": ["meals", "transport"],
        "exclusions": ["insurance"],
        "destination_id": destination.id,
        "itinerary": [
            {
                "day_number": 1,
                "title": "Arrival",
                "description": "Welcome",
                "meals": ["breakfast"],
                "hotel_id": hotel.id,
                "activity_ids": [a.id for a in activities],
            }
        ],
    }

    response = client.post("/tours/", json=payload, headers=auth_headers)
    assert response.status_code == 201

    data = response.json()
    assert data["title"] == payload["title"]
    assert len(data["itinerary"]) == 1

    response = client.get(f"/tours/?page=1&limit=10&city_id={destination.city_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["count"] > 0


def test_list_tours(client):
    response = client.get("/tours/?page=1&limit=10")
    assert response.status_code == 200

    body = response.json()
    assert "data" in body
    assert isinstance(body["data"], list)


def test_get_tour(client, get_test_db):
    tour = get_test_db.query(Tour).first()
    response = client.get(f"/tours/{tour.slug}")

    assert response.status_code in (200, 404)


def test_update_tour(get_test_db, client, auth_headers):
    tour = get_test_db.query(Tour).first()

    update_data = {"title": "Updated Tour Title"}
    response = client.put(f"/tours/{tour.id}", json=update_data, headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["title"] == "Updated Tour Title"


def test_delete_tour(get_test_db, client, auth_headers):
    tour = Tour(
        title="Delete Tour",
        duration="2 days",
        price=90.0,
        destination_id=1,
        slug=slugify("Delete Tour"),
    )
    get_test_db.add(tour)
    get_test_db.commit()

    response = client.delete(f"/tours/{tour.id}", headers=auth_headers)
    assert response.status_code == 204

    response2 = client.get(f"/tours/{tour.id}")
    assert response2.status_code == 404


# --------------------
# TOUR DAY TESTS
# --------------------


def test_create_tour_day(get_test_db, client, auth_headers):
    tour = get_test_db.query(Tour).first()

    payload = {
        "tour_id": tour.id,
        "day_number": 2,
        "title": "Arrival",
        "description": "Welcome",
        "meals": ["breakfast"],
        "activity_ids": [],
        "hotel_id": None,
    }

    response = client.post("/tour-days/", json=payload, headers=auth_headers)
    assert response.status_code == 201


def test_update_tour_day(get_test_db, client, auth_headers):

    day = get_test_db.query(TourDay).first()
    payload = {"title": "New Day Title"}

    response = client.put(f"/tour-days/{day.id}", json=payload, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["title"] == "New Day Title"


def test_remove_activity_from_day(get_test_db, client, auth_headers):
    # Setup
    activities = get_test_db.query(Activity).all()
    tour = get_test_db.query(Tour).first()

    payload = {
        "tour_id": tour.id,
        "day_number": 2,
        "title": "Arrival",
        "description": "Welcome",
        "meals": ["breakfast"],
        "activity_ids": [a.id for a in activities],
        "hotel_id": None,
    }
    activity = activities[0]

    response = client.post("/tour-days/", json=payload, headers=auth_headers).json()
    day_id = response["id"]

    delete_response = client.delete(
        f"/tour-days/{day_id}/activities/{activity.id}", headers=auth_headers
    )
    print(response)
    assert delete_response.status_code == 200
    assert len(get_test_db.get(TourDay, day_id).activities) < len(
        response["activities"]
    )
