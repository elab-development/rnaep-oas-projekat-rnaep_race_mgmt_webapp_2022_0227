from app.db import repository
from tests.conftest import TestSessionLocal

USER_ONE = {"sub": "10", "role": "participant", "email": "one@example.com", "username": "User One"}
USER_TWO = {"sub": "11", "role": "participant", "email": "two@example.com", "username": "User Two"}


async def _create_payment(user_id: int, registration_id: int, stripe_session_id: str) -> int:
    async with TestSessionLocal() as db:
        payment = await repository.create_payment(
            db=db,
            user_id=user_id,
            registration_id=registration_id,
            stripe_session_id=stripe_session_id,
            amount=25.0,
            participant_email="p@example.com",
            participant_name="Participant",
        )
        return payment.id


async def test_get_my_payments_returns_only_own(client, login_as):
    await _create_payment(int(USER_ONE["sub"]), registration_id=1, stripe_session_id="cs_1")
    await _create_payment(int(USER_TWO["sub"]), registration_id=2, stripe_session_id="cs_2")

    login_as(USER_ONE)
    resp = await client.get("/payments/me")

    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 1
    assert body[0]["user_id"] == int(USER_ONE["sub"])


async def test_get_payment_by_id_rejects_non_owner(client, login_as):
    payment_id = await _create_payment(int(USER_ONE["sub"]), registration_id=1, stripe_session_id="cs_1")

    login_as(USER_TWO)
    resp = await client.get(f"/payments/{payment_id}")
    assert resp.status_code == 403


async def test_get_payment_by_id_returns_owner_payment(client, login_as):
    payment_id = await _create_payment(int(USER_ONE["sub"]), registration_id=1, stripe_session_id="cs_1")

    login_as(USER_ONE)
    resp = await client.get(f"/payments/{payment_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == payment_id


async def test_get_payment_by_id_returns_404_for_unknown_id(client, login_as):
    login_as(USER_ONE)
    resp = await client.get("/payments/999")
    assert resp.status_code == 404
