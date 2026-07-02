from unittest.mock import Mock
from types import SimpleNamespace

import pytest

from app.db import repository
from app.kafka import consumer
from tests.conftest import TestSessionLocal


@pytest.fixture(autouse=True)
def _consumer_uses_test_db(monkeypatch):
    monkeypatch.setattr(consumer, "SessionLocal", TestSessionLocal)


async def test_handle_registration_created_creates_a_payment(monkeypatch):
    create_mock = Mock(
        return_value=SimpleNamespace(id="cs_test_created", url="https://checkout.stripe.com/created")
    )
    monkeypatch.setattr("app.service.stripe.checkout.Session.create", create_mock)

    await consumer.handle_registration_created(
        {
            "participant_id": 10,
            "id": 1,
            "amount": 25.0,
            "participant_email": "p@example.com",
            "participant_name": "Participant",
        }
    )

    async with TestSessionLocal() as db:
        payment = await repository.get_payment_by_registration_id(db, 1)
        assert payment is not None
        assert payment.user_id == 10
        assert payment.checkout_url == "https://checkout.stripe.com/created"


async def test_handle_registration_deleted_removes_the_payment():
    async with TestSessionLocal() as db:
        await repository.create_payment(
            db=db,
            user_id=10,
            registration_id=5,
            stripe_session_id="cs_to_delete",
            amount=25.0,
            participant_email="p@example.com",
            participant_name="Participant",
        )

    await consumer.handle_registration_deleted({"registration_id": 5})

    async with TestSessionLocal() as db:
        payment = await repository.get_payment_by_registration_id(db, 5)
        assert payment is None
