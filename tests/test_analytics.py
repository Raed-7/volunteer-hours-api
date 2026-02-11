from datetime import datetime, timedelta

from fastapi.testclient import TestClient


def test_leaderboard_and_awards(client: TestClient, auth_token: str) -> None:
    headers = {"Authorization": f"Bearer {auth_token}"}

    v1 = client.post("/volunteers", json={"full_name": "Top Volunteer"}, headers=headers).json()
    v2 = client.post("/volunteers", json={"full_name": "Mid Volunteer"}, headers=headers).json()

    event = client.post(
        "/events",
        json={
            "title": "Marathon",
            "event_category": "sports",
            "event_date": "2026-02-01",
            "location": "City",
        },
        headers=headers,
    ).json()

    start = datetime(2026, 2, 1, 8, 0, 0)
    shift = client.post(
        f"/events/{event['id']}/shifts",
        json={"title": "Day", "start_time": start.isoformat(), "end_time": (start + timedelta(hours=10)).isoformat()},
        headers=headers,
    ).json()

    client.post(
        f"/shifts/{shift['id']}/check-in",
        json={"volunteer_id": v1["id"], "checked_in_at": start.isoformat()},
        headers=headers,
    )
    client.post(
        f"/shifts/{shift['id']}/check-out",
        json={"volunteer_id": v1["id"], "checked_out_at": (start + timedelta(hours=20)).isoformat()},
        headers=headers,
    )

    client.post(
        f"/shifts/{shift['id']}/check-in",
        json={"volunteer_id": v2["id"], "checked_in_at": start.isoformat()},
        headers=headers,
    )
    client.post(
        f"/shifts/{shift['id']}/check-out",
        json={"volunteer_id": v2["id"], "checked_out_at": (start + timedelta(hours=16)).isoformat()},
        headers=headers,
    )

    leaderboard = client.get("/analytics/leaderboard", headers=headers)
    assert leaderboard.status_code == 200
    rows = leaderboard.json()
    assert rows[0]["volunteer_id"] == v1["id"]
    assert rows[0]["total_hours"] == 20.0

    awards = client.get("/analytics/awards", headers=headers)
    assert awards.status_code == 200
    tiers = {item["volunteer_id"]: item["tier"] for item in awards.json()}
    assert tiers[v1["id"]] == "Tier A"
    assert tiers[v2["id"]] == "Tier B"
