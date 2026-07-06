from datetime import datetime, timedelta, timezone

ORGANISER = {"sub": "1", "role": "organiser", "email": "org@example.com", "username": "Org One"}
OTHER_ORGANISER = {"sub": "2", "role": "organiser", "email": "org2@example.com", "username": "Org Two"}
PARTICIPANT = {"sub": "10", "role": "participant", "email": "p@example.com", "username": "Part One"}
OTHER_PARTICIPANT = {"sub": "11", "role": "participant", "email": "p2@example.com", "username": "Part Two"}


def make_race_payload(**overrides):
    now = datetime.now(timezone.utc)
    data = {
        "name": "Belgrade Marathon",
        "date_time": (now + timedelta(days=30)).isoformat(),
        "deadline": (now + timedelta(days=20)).isoformat(),
        "location": "Belgrade",
        "max_participants": 2,
        "price": 25.0,
    }
    data.update(overrides)
    return data


async def create_race(client, login_as, **overrides) -> int:
    login_as(ORGANISER)
    resp = await client.post("/api/race/", json=make_race_payload(**overrides))
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]
