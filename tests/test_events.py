from fastapi.testclient import TestClient


def test_list_event_shifts_404_for_missing_event(client: TestClient, auth_token: str) -> None:
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/events/9999/shifts", headers=headers)
    assert response.status_code == 404
