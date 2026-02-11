from datetime import datetime, timedelta

from fastapi.testclient import TestClient


def test_checkin_checkout_rules(client: TestClient, auth_token: str) -> None:
    headers = {"Authorization": f"Bearer {auth_token}"}

    volunteer = client.post("/volunteers", json={"full_name": "Attendee"}, headers=headers).json()
    event = client.post(
        "/events",
        json={
            "title": "Food Drive",
            "event_category": "community",
            "event_date": "2026-01-01",
            "location": "Hall",
        },
        headers=headers,
    ).json()

    start = datetime(2026, 1, 1, 9, 0, 0)
    end = datetime(2026, 1, 1, 12, 0, 0)
    shift = client.post(
        f"/events/{event['id']}/shifts",
        json={"title": "Morning", "start_time": start.isoformat(), "end_time": end.isoformat(), "required_volunteers": 2},
        headers=headers,
    ).json()

    early_checkout = client.post(
        f"/shifts/{shift['id']}/check-out",
        json={"volunteer_id": volunteer["id"]},
        headers=headers,
    )
    assert early_checkout.status_code == 400

    checkin_time = start
    checkin = client.post(
        f"/shifts/{shift['id']}/check-in",
        json={"volunteer_id": volunteer["id"], "checked_in_at": checkin_time.isoformat()},
        headers=headers,
    )
    assert checkin.status_code == 201

    duplicate_checkin = client.post(
        f"/shifts/{shift['id']}/check-in",
        json={"volunteer_id": volunteer["id"], "checked_in_at": checkin_time.isoformat()},
        headers=headers,
    )
    assert duplicate_checkin.status_code == 400

    invalid_checkout = client.post(
        f"/shifts/{shift['id']}/check-out",
        json={"volunteer_id": volunteer["id"], "checked_out_at": (checkin_time - timedelta(minutes=1)).isoformat()},
        headers=headers,
    )
    assert invalid_checkout.status_code == 400

    valid_checkout = client.post(
        f"/shifts/{shift['id']}/check-out",
        json={"volunteer_id": volunteer["id"], "checked_out_at": (checkin_time + timedelta(hours=2)).isoformat()},
        headers=headers,
    )
    assert valid_checkout.status_code == 200
    assert valid_checkout.json()["minutes_worked"] == 120
