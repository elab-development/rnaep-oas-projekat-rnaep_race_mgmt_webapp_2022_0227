from unittest.mock import AsyncMock

import pytest

from app.enum import PaymentStatusEnum
from app.kafka import consumer
from tests.conftest import TestSessionLocal
from tests.helpers import PARTICIPANT, create_race


@pytest.fixture(autouse=True)
def _consumer_uses_test_db(monkeypatch):
    # handle_payment_* open their own `async with SessionLocal()` rather than going
    # through FastAPI's dependency-injected get_db, so they need to be pointed at the
    # same in-memory test database the HTTP-layer tests use.
    monkeypatch.setattr(consumer, "SessionLocal", TestSessionLocal)


async def _create_registration(client, login_as) -> int:
    race_id = await create_race(client, login_as)
    login_as(PARTICIPANT)
    resp = await client.post("/api/registration/", json={"race_id": race_id})
    assert resp.status_code == 201
    return resp.json()["id"]


async def test_handle_payment_completed_marks_registration_completed(client, login_as, monkeypatch):
    registration_id = await _create_registration(client, login_as)
    send_confirmed = AsyncMock()
    monkeypatch.setattr(consumer, "send_registration_confirmed_email", send_confirmed)

    await consumer.handle_payment_completed(
        {
            "registration_id": registration_id,
            "participant_email": PARTICIPANT["email"],
            "participant_name": PARTICIPANT["username"],
        }
    )

    async with TestSessionLocal() as db:
        from app.db.repositories.registration_repository import get_registration_by_id

        registration = await get_registration_by_id(db, registration_id)
        assert registration.payment_status == PaymentStatusEnum.COMPLETED

    send_confirmed.assert_awaited_once()


async def test_handle_payment_failed_marks_registration_failed(client, login_as, monkeypatch):
    registration_id = await _create_registration(client, login_as)
    send_failed = AsyncMock()
    monkeypatch.setattr(consumer, "send_registration_failed_email", send_failed)

    await consumer.handle_payment_failed(
        {
            "registration_id": registration_id,
            "participant_email": PARTICIPANT["email"],
            "participant_name": PARTICIPANT["username"],
        }
    )

    async with TestSessionLocal() as db:
        from app.db.repositories.registration_repository import get_registration_by_id

        registration = await get_registration_by_id(db, registration_id)
        assert registration.payment_status == PaymentStatusEnum.FAILED

    send_failed.assert_awaited_once()


async def test_handle_payment_completed_skips_email_without_participant_email(client, login_as, monkeypatch):
    registration_id = await _create_registration(client, login_as)
    send_confirmed = AsyncMock()
    monkeypatch.setattr(consumer, "send_registration_confirmed_email", send_confirmed)

    await consumer.handle_payment_completed({"registration_id": registration_id})

    send_confirmed.assert_not_awaited()


async def test_handle_payment_completed_for_unknown_registration_is_a_noop(monkeypatch):
    send_confirmed = AsyncMock()
    monkeypatch.setattr(consumer, "send_registration_confirmed_email", send_confirmed)

    await consumer.handle_payment_completed({"registration_id": 999999})

    send_confirmed.assert_not_awaited()
