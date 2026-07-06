from unittest.mock import Mock

import stripe

from app.db import repository
from app.enum import PaymentStatusEnum
from tests.conftest import TestSessionLocal


async def _create_payment(stripe_session_id: str) -> int:
    async with TestSessionLocal() as db:
        payment = await repository.create_payment(
            db=db,
            user_id=10,
            registration_id=1,
            stripe_session_id=stripe_session_id,
            amount=25.0,
            participant_email="p@example.com",
            participant_name="Participant",
        )
        return payment.id


def _fake_event(event_type: str, session_id: str) -> dict:
    return {"type": event_type, "data": {"object": {"id": session_id}}}


async def test_webhook_rejects_invalid_signature(client, monkeypatch):
    monkeypatch.setattr(
        "app.service.stripe.Webhook.construct_event",
        Mock(side_effect=stripe.SignatureVerificationError("bad signature", "sig")),
    )

    resp = await client.post(
        "/payments/webhook",
        content=b"{}",
        headers={"stripe-signature": "invalid"},
    )
    assert resp.status_code == 400


async def test_webhook_completed_marks_payment_completed(client, monkeypatch):
    await _create_payment("cs_completed_1")
    monkeypatch.setattr(
        "app.service.stripe.Webhook.construct_event",
        Mock(return_value=_fake_event("checkout.session.completed", "cs_completed_1")),
    )
    resp = await client.post(
        "/payments/webhook",
        content=b"{}",
        headers={"stripe-signature": "valid"},
    )
    assert resp.status_code == 200

    async with TestSessionLocal() as db:
        payment = await repository.get_payment_by_stripe_session_id(db, "cs_completed_1")
        assert payment.status == PaymentStatusEnum.COMPLETED


async def test_webhook_expired_marks_payment_failed(client, monkeypatch):
    await _create_payment("cs_expired_1")
    monkeypatch.setattr(
        "app.service.stripe.Webhook.construct_event",
        Mock(return_value=_fake_event("checkout.session.expired", "cs_expired_1")),
    )

    resp = await client.post(
        "/payments/webhook",
        content=b"{}",
        headers={"stripe-signature": "valid"},
    )
    assert resp.status_code == 200

    async with TestSessionLocal() as db:
        payment = await repository.get_payment_by_stripe_session_id(db, "cs_expired_1")
        assert payment.status == PaymentStatusEnum.FAILED


async def test_webhook_for_unknown_session_id_is_a_noop(client, monkeypatch):
    monkeypatch.setattr(
        "app.service.stripe.Webhook.construct_event",
        Mock(return_value=_fake_event("checkout.session.completed", "cs_does_not_exist")),
    )

    resp = await client.post(
        "/payments/webhook",
        content=b"{}",
        headers={"stripe-signature": "valid"},
    )
    assert resp.status_code == 200
