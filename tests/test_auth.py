from fastapi.testclient import TestClient


def test_auth_login_and_protected_requires_token(client: TestClient) -> None:
    register = client.post(
        "/auth/register",
        json={"name": "Org", "email": "org@example.com", "password": "password123", "role": "organiser"},
    )
    assert register.status_code == 201

    protected = client.get("/volunteers")
    assert protected.status_code == 401

    login = client.post("/auth/login", json={"email": "org@example.com", "password": "password123"})
    assert login.status_code == 200
    token = login.json()["access_token"]

    ok = client.get("/volunteers", headers={"Authorization": f"Bearer {token}"})
    assert ok.status_code == 200
