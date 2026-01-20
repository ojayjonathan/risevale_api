from starlette.testclient import TestClient

from app.core.config import Settings
from app.models import User


def test_login(settings: Settings, get_user: User, client: TestClient):
    response = client.post(
        "/auth/login/",
        json={
            "password": settings.TEST_USER_PASSWORD,
            "email": settings.TEST_USER_EMAIL,
        },
    )
    assert response.status_code == 200
