from unittest.mock import Mock
from types import SimpleNamespace

from httpx import ASGITransport, AsyncClient

from main import app

PARTICIPANT = {"sub": "10", "role": "participant", "email": "p@example.com", "username": "Part One"}


async def test_checkout_rejected_without_csrf_token(login_as):
    login_as(PARTICIPANT)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post("/payments/checkout", json={"registration_id": 1, "amount": 25.0})
    assert resp.status_code == 403


async def test_checkout_succeeds_with_matching_csrf_token(login_as, monkeypatch):
    login_as(PARTICIPANT)
    monkeypatch.setattr(
        "app.service.stripe.checkout.Session.create",
        Mock(return_value=SimpleNamespace(id="cs_test_csrf", url="https://checkout.stripe.com/csrf")),
    )
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        cookies={"csrf_token": "matching-value"},
        headers={"X-CSRF-Token": "matching-value"},
    ) as ac:
        resp = await ac.post("/payments/checkout", json={"registration_id": 1, "amount": 25.0})
    assert resp.status_code == 200


async def test_webhook_does_not_require_csrf_token(monkeypatch):
    # Stripe calls this server-to-server; it never carries our browser cookies.
    import stripe

    monkeypatch.setattr(
        "app.service.stripe.Webhook.construct_event",
        Mock(side_effect=stripe.SignatureVerificationError("bad signature", "sig")),
    )
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post(
            "/payments/webhook", content=b"{}", headers={"stripe-signature": "invalid"}
        )
    # Reaches the handler (400 for bad signature) rather than being blocked at 403 by CSRF.
    assert resp.status_code == 400
