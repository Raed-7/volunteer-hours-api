from fastapi.testclient import TestClient


def test_event_crud(client: TestClient, auth_token: str) -> None:
    headers = {"Authorization": f"Bearer {auth_token}"}

    create = client.post(
        "/events",
        json={
            "title": "Campus Open Day",
            "event_category": "Outreach",
            "event_date": "2026-03-10",
            "location": "Main Hall",
            "description": "Welcome visitors",
        },
        headers=headers,
    )
    assert create.status_code == 201
    event_id = create.json()["id"]

    list_resp = client.get("/events", headers=headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1

    update = client.patch(f"/events/{event_id}", json={"location": "Science Block"}, headers=headers)
    assert update.status_code == 200
    assert update.json()["location"] == "Science Block"

    delete = client.delete(f"/events/{event_id}", headers=headers)
    assert delete.status_code == 204

    missing = client.get(f"/events/{event_id}", headers=headers)
    assert missing.status_code == 404
