from tests.helpers import (
    ORGANISER,
    OTHER_ORGANISER,
    PARTICIPANT,
    create_race,
    make_race_payload,
)


async def test_get_race_requires_authentication(client, login_as):
    race_id = await create_race(client, login_as)

    login_as(None)
    resp = await client.get(f"/api/race/{race_id}")
    assert resp.status_code == 401


async def test_get_race_returns_404_for_unknown_id(client, login_as):
    login_as(PARTICIPANT)
    resp = await client.get("/api/race/999")
    assert resp.status_code == 404


async def test_get_race_returns_race_when_authenticated(client, login_as):
    race_id = await create_race(client, login_as)

    login_as(PARTICIPANT)
    resp = await client.get(f"/api/race/{race_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == race_id


async def test_create_race_requires_organiser_role(client, login_as):
    login_as(PARTICIPANT)
    resp = await client.post("/api/race/", json=make_race_payload())
    assert resp.status_code == 403


async def test_organiser_can_create_race(client, login_as):
    login_as(ORGANISER)
    resp = await client.post("/api/race/", json=make_race_payload())
    assert resp.status_code == 201
    assert resp.json()["organiser_id"] == int(ORGANISER["sub"])


async def test_create_race_rejects_deadline_after_race_date(client, login_as):
    login_as(ORGANISER)
    payload = make_race_payload()
    payload["deadline"], payload["date_time"] = payload["date_time"], payload["deadline"]
    resp = await client.post("/api/race/", json=payload)
    assert resp.status_code == 400


async def test_create_race_rejects_non_positive_max_participants(client, login_as):
    login_as(ORGANISER)
    resp = await client.post("/api/race/", json=make_race_payload(max_participants=0))
    assert resp.status_code == 400


async def test_patch_race_rejects_non_owner(client, login_as):
    race_id = await create_race(client, login_as)

    login_as(OTHER_ORGANISER)
    resp = await client.patch(f"/api/race/{race_id}", json={"name": "Hijacked"})
    assert resp.status_code == 403


async def test_owner_can_patch_race(client, login_as):
    race_id = await create_race(client, login_as)

    login_as(ORGANISER)
    resp = await client.patch(f"/api/race/{race_id}", json={"name": "Updated Marathon"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated Marathon"


async def test_delete_race_without_registrations_succeeds(client, login_as):
    race_id = await create_race(client, login_as)

    login_as(ORGANISER)
    resp = await client.delete(f"/api/race/{race_id}")
    assert resp.status_code == 204


async def test_delete_race_with_pending_registration_is_blocked(client, login_as):
    # A pending (unpaid) registration still reserves a spot, so deleting the race
    # out from under it must be blocked just like a completed registration.
    race_id = await create_race(client, login_as)

    login_as(PARTICIPANT)
    reg_resp = await client.post("/api/registration/", json={"race_id": race_id})
    assert reg_resp.status_code == 201

    login_as(ORGANISER)
    resp = await client.delete(f"/api/race/{race_id}")
    assert resp.status_code == 403


async def test_delete_race_with_only_failed_registrations_is_allowed(client, login_as):
    from app.enum import PaymentStatusEnum
    from app.db.repositories.registration_repository import update_registration_payment_status
    from tests.conftest import TestSessionLocal

    race_id = await create_race(client, login_as)

    login_as(PARTICIPANT)
    reg_resp = await client.post("/api/registration/", json={"race_id": race_id})
    registration_id = reg_resp.json()["id"]

    async with TestSessionLocal() as db:
        await update_registration_payment_status(db, registration_id, PaymentStatusEnum.FAILED)

    login_as(ORGANISER)
    resp = await client.delete(f"/api/race/{race_id}")
    assert resp.status_code == 204


async def test_delete_race_with_completed_registration_is_blocked(client, login_as):
    from app.enum import PaymentStatusEnum
    from tests.conftest import TestSessionLocal

    race_id = await create_race(client, login_as)

    login_as(PARTICIPANT)
    reg_resp = await client.post("/api/registration/", json={"race_id": race_id})
    registration_id = reg_resp.json()["id"]

    from app.db.repositories.registration_repository import update_registration_payment_status

    async with TestSessionLocal() as db:
        await update_registration_payment_status(db, registration_id, PaymentStatusEnum.COMPLETED)

    login_as(ORGANISER)
    resp = await client.delete(f"/api/race/{race_id}")
    assert resp.status_code == 403
