from fastapi.testclient import TestClient
from app.main import app


def test_customer_cannot_access_another_customer():
    with TestClient(app) as client:
        # Create the demo account if it doesn't already exist.
        registration = client.post(
            "/auth/register",
            json={
                "email": "john@example.com",
                "password": "StrongPassword123!",
            },
        )

        assert registration.status_code in [200, 409]

        login = client.post(
            "/auth/login",
            json={
                "email": "john@example.com",
                "password": "StrongPassword123!",
            },
        )

        assert login.status_code == 200

        token = login.json()["access_token"]

        response = client.get(
            "/customers/CUST002",
            headers={
                "Authorization": f"Bearer {token}"
            },
        )

        assert response.status_code == 403