# ---------------------------------------------------------
# Helper to create an activity
# ---------------------------------------------------------
from app.tests.conftest import get_test_db, auth_headers


def create_test_activity(get_test_db, client, auth_headers):
    payload = {
        "title": "Hiking",
        "type": "included",
        "description": "Mountain hike",
        "image": "hike.jpg",
        "destination_id": 1,
        "is_active": True,
    }
    response = client.post("/activities", json=payload, headers=auth_headers)
    assert response.status_code == 201
    return response.json()


# ---------------------------------------------------------
# TESTS
# ---------------------------------------------------------


def test_list_activities_empty(get_test_db, client):
    response = client.get("/activities/?page=1&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert data["data"] == []


def test_create_activity(get_test_db, client, auth_headers):
    payload = {
        "title": "Safari",
        "type": "optional",
        "description": "Wildlife safari",
        "image": "safari.jpg",
        "destination_id": 1,
        "is_active": True,
    }

    response = client.post("/activities", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()

    assert data["title"] == "Safari"
    assert data["type"] == "optional"
    assert data["is_active"] is True


def test_list_activities_with_filter(get_test_db, client):
    client.post(
        "/activities/",
        json={
            "title": "Diving",
            "type": "optional",
            "description": "Sea diving",
            "image": None,
            "destination_id": 1,
            "is_active": True,
        },
    )

    resp = client.get("/activities/?activity_type=optional")
    assert resp.status_code == 200
    data = resp.json()

    # Pagination schema
    assert "data" in data


def test_get_activity(get_test_db, client, auth_headers):
    created = create_test_activity(get_test_db, client, auth_headers)
    act_id = created["id"]

    response = client.get(f"/activities/{act_id}")
    assert response.status_code == 200
    data = response.json()

    assert data["id"] == act_id
    assert data["title"] == created["title"]


def test_update_activity(get_test_db, client, auth_headers):
    created = create_test_activity(get_test_db, client, auth_headers)
    act_id = created["id"]

    update_data = {
        "title": "Updated Hiking",
        "type": "included",
        "description": "Updated desc",
        "image": "updated.jpg",
        "destination_id": 1,
        "is_active": True,
    }

    response = client.put(
        f"/activities/{act_id}", json=update_data, headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()

    assert data["title"] == "Updated Hiking"
    assert data["description"] == "Updated desc"


def test_delete_activity(get_test_db, client, auth_headers):
    created = create_test_activity(get_test_db, client, auth_headers)
    act_id = created["id"]

    response = client.delete(f"/activities/{act_id}")
    assert response.status_code == 204

    # Should now return 404
    r = client.get(f"/activities/{act_id}")
    assert r.status_code == 404
