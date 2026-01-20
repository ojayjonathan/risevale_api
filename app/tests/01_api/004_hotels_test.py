import io

from app.models.hotel import Hotel


def test_create_hotel(
    client,
    get_test_db,
    auth_headers,
):
    # Prepare form data
    form_data = {
        "name": "Grand Palace Hotel",
        "category": "Luxury",
        "rating": 4.5,
        "reviews_count": 120,
        "price_per_night": 270.00,
        "description": "Amazing stay",
        "bedrooms": 2,
        "max_guests": 4,
        "amenities": "wifi,pool",
        "city_id": 1,
    }

    files = {"images": ("img1.jpg", io.BytesIO(b"dummy image"), "image/jpeg")}

    response = client.post(
        "/hotels/", data=form_data, files=files, headers=auth_headers
    )
    data = response.json()
    print(data)
    assert response.status_code == 201

    assert data["name"] == form_data["name"]
    assert "id" in data


def test_list_hotels(client):
    response = client.get("/hotels/?page=1&limit=10")
    assert response.status_code == 200
    body = response.json()

    assert "count" in body
    assert "data" in body
    assert isinstance(body["data"], list)


def test_get_hotel(client, get_test_db):
    # Create hotel first
    hotel = get_test_db.query(Hotel).first()

    response = client.get(f"/hotels/{hotel.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == hotel.id
    assert data["name"] == hotel.name


def test_update_hotel(client, get_test_db, auth_headers):
    # Create hotel first
    hotel = get_test_db.query(Hotel).first()

    # Prepare form-data update
    update_form = {
        "name": "Updated Name",
        "rating": 4.2,
        "amenities": "wifi,spa",
    }

    files = {"images": ("new_img.jpg", io.BytesIO(b"new image"), "image/jpeg")}

    response = client.put(
        f"/hotels/{hotel.id}", data=update_form, files=files, headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()

    assert data["name"] == "Updated Name"
    assert data["rating"] == 4.2
    assert "images" in data


def test_delete_hotel(client, get_test_db, auth_headers):
    # Create hotel first
    hotel = Hotel(name="Delete Me", price_per_night=100.0, city_id=1, country_id=1)
    get_test_db.add(hotel)
    get_test_db.commit()
    get_test_db.refresh(hotel)

    response = client.delete(f"/hotels/{hotel.id}", headers=auth_headers)
    assert response.status_code == 204

    # Ensure deleted
    response2 = client.get(f"/hotels/{hotel.id}")
    assert response2.status_code == 404
