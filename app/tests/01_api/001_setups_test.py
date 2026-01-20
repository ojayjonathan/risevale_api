from app.tests.conftest import get_test_db, get_country


def test_create_city(client, get_test_db, get_country, auth_headers):
    payload = {"name": "Nakuru", "country_id": get_country.id}
    response = client.post("/setups/cities/", json=payload, headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Nakuru"
    assert data["country_id"] == get_country.id


def test_get_countries(client, get_test_db):

    response = client.get("/setups/countries/")
    assert response.status_code == 200

    data = response.json()
    assert len(data) > 0
    assert data[0]["name"] == "Kenya"


def test_get_cities(client, get_test_db, get_country, get_city):
    response = client.get("/setups/cities/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0

    response = client.get("/setups/cities/?q=Nai")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1

    response = client.get(f"/setups/cities/?country_id={get_country.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0


def test_update_city(client, get_test_db, get_country, get_city, auth_headers):
    payload = {"name": "Mombase", "country_id": get_country.id}

    response = client.put(
        f"/setups/cities/{get_city.id}", json=payload, headers=auth_headers
    )
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Mombase"
