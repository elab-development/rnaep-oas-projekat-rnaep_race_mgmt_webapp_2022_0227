from datetime import datetime, timedelta, timezone

from tests.helpers import (
    ORGANISER,
    OTHER_ORGANISER,
    OTHER_PARTICIPANT,
    PARTICIPANT,
    create_race,
    make_race_payload,
)


async def test_create_registration_requires_participant_role(client, login_as):
    race_id = await create_race(client, login_as)

    login_as(ORGANISER)
    resp = await client.post("/api/registration/", json={"race_id": race_id})
    assert resp.status_code == 403


async def test_participant_can_register_for_race(client, login_as):
    race_id = await create_race(client, login_as)

    login_as(PARTICIPANT)
    resp = await client.post("/api/registration/", json={"race_id": race_id})
    assert resp.status_code == 201
    body = resp.json()
    assert body["payment_status"] == "pending"
    assert body["bib_number"]
    assert body["participant_id"] == int(PARTICIPANT["sub"])


async def test_duplicate_registration_rejected(client, login_as):
    race_id = await create_race(client, login_as)

    login_as(PARTICIPANT)
    await client.post("/api/registration/", json={"race_id": race_id})
    resp = await client.post("/api/registration/", json={"race_id": race_id})
    assert resp.status_code == 400


async def test_pending_registrations_do_not_count_against_capacity(client, login_as):
    # get_registration_count_by_race only counts COMPLETED registrations, so
    # merely-pending (unpaid) signups don't currently trigger the "race is full"
    # check, even past max_participants. This documents that actual behavior.
    race_id = await create_race(client, login_as, max_participants=1)

    login_as(PARTICIPANT)
    first = await client.post("/api/registration/", json={"race_id": race_id})
    assert first.status_code == 201

    login_as(OTHER_PARTICIPANT)
    second = await client.post("/api/registration/", json={"race_id": race_id})
    assert second.status_code == 201


async def test_registration_rejected_when_race_is_full(client, login_as):
    from app.enum import PaymentStatusEnum
    from app.db.repositories.registration_repository import update_registration_payment_status
    from tests.conftest import TestSessionLocal

    race_id = await create_race(client, login_as, max_participants=1)

    login_as(PARTICIPANT)
    first = await client.post("/api/registration/", json={"race_id": race_id})
    assert first.status_code == 201

    async with TestSessionLocal() as db:
        await update_registration_payment_status(db, first.json()["id"], PaymentStatusEnum.COMPLETED)

    login_as(OTHER_PARTICIPANT)
    second = await client.post("/api/registration/", json={"race_id": race_id})
    assert second.status_code == 400


async def test_registration_rejected_after_deadline(client, login_as):
    now = datetime.now(timezone.utc)
    race_id = await create_race(
        client,
        login_as,
        date_time=(now + timedelta(days=2)).isoformat(),
        deadline=(now - timedelta(hours=1)).isoformat(),
    )

    login_as(PARTICIPANT)
    resp = await client.post("/api/registration/", json={"race_id": race_id})
    assert resp.status_code == 400


async def test_registration_rejected_for_unknown_race(client, login_as):
    login_as(PARTICIPANT)
    resp = await client.post("/api/registration/", json={"race_id": 999})
    assert resp.status_code == 404


async def test_delete_registration_rejects_non_owner(client, login_as):
    race_id = await create_race(client, login_as)

    login_as(PARTICIPANT)
    create_resp = await client.post("/api/registration/", json={"race_id": race_id})
    registration_id = create_resp.json()["id"]

    login_as(OTHER_PARTICIPANT)
    resp = await client.delete(f"/api/registration/{registration_id}")
    assert resp.status_code == 403


async def test_owner_can_delete_pending_registration(client, login_as):
    race_id = await create_race(client, login_as)

    login_as(PARTICIPANT)
    create_resp = await client.post("/api/registration/", json={"race_id": race_id})
    registration_id = create_resp.json()["id"]

    resp = await client.delete(f"/api/registration/{registration_id}")
    assert resp.status_code == 204


async def test_get_registrations_by_race_requires_owner_organiser(client, login_as):
    race_id = await create_race(client, login_as)

    login_as(PARTICIPANT)
    await client.post("/api/registration/", json={"race_id": race_id})

    login_as(OTHER_ORGANISER)
    resp = await client.get("/api/registration/", params={"race_id": race_id})
    assert resp.status_code == 403


async def test_owner_organiser_can_list_race_registrations(client, login_as):
    race_id = await create_race(client, login_as)

    login_as(PARTICIPANT)
    await client.post("/api/registration/", json={"race_id": race_id})

    login_as(ORGANISER)
    resp = await client.get("/api/registration/", params={"race_id": race_id})
    assert resp.status_code == 200
    assert len(resp.json()) == 1


async def test_get_my_registrations_returns_only_own(client, login_as):
    race_id = await create_race(client, login_as)

    login_as(PARTICIPANT)
    await client.post("/api/registration/", json={"race_id": race_id})

    resp = await client.get("/api/registration/myregistrations")
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["participant_id"] == int(PARTICIPANT["sub"])
