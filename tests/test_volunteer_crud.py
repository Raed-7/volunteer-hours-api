from fastapi.testclient import TestClient


def test_volunteer_crud(client: TestClient, auth_token: str) -> None:
    headers = {"Authorization": f"Bearer {auth_token}"}

    create = client.post(
        "/volunteers",
        json={"full_name": "Jane Doe", "email": "jane@example.com", "phone": "1234", "notes": "Reliable"},
        headers=headers,
    )
    assert create.status_code == 201
    volunteer_id = create.json()["id"]

    list_resp = client.get("/volunteers", headers=headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1

    update = client.patch(f"/volunteers/{volunteer_id}", json={"phone": "5678"}, headers=headers)
    assert update.status_code == 200
    assert update.json()["phone"] == "5678"

    delete = client.delete(f"/volunteers/{volunteer_id}", headers=headers)
    assert delete.status_code == 204

    missing = client.get(f"/volunteers/{volunteer_id}", headers=headers)
    assert missing.status_code == 404
