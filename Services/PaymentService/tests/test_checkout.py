from types import SimpleNamespace
from unittest.mock import Mock

import stripe

PARTICIPANT = {"sub": "10", "role": "participant", "email": "p@example.com", "username": "Part One"}
ORGANISER = {"sub": "1", "role": "organiser", "email": "org@example.com", "username": "Org One"}


def _fake_session(session_id="cs_test_123", url="https://checkout.stripe.com/test_123"):
    return SimpleNamespace(id=session_id, url=url)


async def test_checkout_requires_participant_role(client, login_as):
    login_as(ORGANISER)
    resp = await client.post("/payments/checkout", json={"registration_id": 1, "amount": 25.0})
    assert resp.status_code == 403


async def test_checkout_creates_stripe_session(client, login_as, monkeypatch):
    create_mock = Mock(return_value=_fake_session())
    monkeypatch.setattr("app.service.stripe.checkout.Session.create", create_mock)

    login_as(PARTICIPANT)
    resp = await client.post("/payments/checkout", json={"registration_id": 1, "amount": 25.0})

    assert resp.status_code == 200
    assert resp.json()["checkout_url"] == "https://checkout.stripe.com/test_123"
    create_mock.assert_called_once()


async def test_checkout_reuses_existing_payment_for_same_registration(client, login_as, monkeypatch):
    create_mock = Mock(return_value=_fake_session())
    monkeypatch.setattr("app.service.stripe.checkout.Session.create", create_mock)

    login_as(PARTICIPANT)
    first = await client.post("/payments/checkout", json={"registration_id": 1, "amount": 25.0})
    second = await client.post("/payments/checkout", json={"registration_id": 1, "amount": 25.0})

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["checkout_url"] == second.json()["checkout_url"]
    create_mock.assert_called_once()


async def test_checkout_returns_502_on_stripe_error(client, login_as, monkeypatch):
    create_mock = Mock(side_effect=stripe.StripeError("card network unreachable"))
    monkeypatch.setattr("app.service.stripe.checkout.Session.create", create_mock)

    login_as(PARTICIPANT)
    resp = await client.post("/payments/checkout", json={"registration_id": 2, "amount": 10.0})

    assert resp.status_code == 502
