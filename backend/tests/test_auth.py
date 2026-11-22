from fastapi.testclient import TestClient
from app.main import app


def test_unauthenticated_access():
    with TestClient(app) as client:
        response = client.get("/auth/me")
        assert response.status_code in [401, 403]


def test_login():
    with TestClient(app) as client:
        registration = client.post(
        "/auth/register",
        json={
            "email": "john@example.com",
            "password": "StrongPassword123!",
        },
    )

    assert registration.status_code in [200, 409]

    response = client.post(
        "/auth/login",
        json={
            "email": "john@example.com",
            "password": "StrongPassword123!",
        },
    )

    assert response.status_code == 200
    assert "access_token" in response.json()