from unittest.mock import Mock
from types import SimpleNamespace

import stripe
from aiobreaker import CircuitBreakerState

from app.service import stripe_checkout_breaker

PARTICIPANT = {"sub": "10", "role": "participant", "email": "p@example.com", "username": "Part One"}


def _failing_mock(exception: Exception) -> Mock:
    mock = Mock(side_effect=exception)
    # aiobreaker's CircuitBreaker.call() checks `func._ignore_on_call` to avoid
    # double-tripping when wrapping its own decorated functions. A bare Mock
    # auto-vivifies that attribute as a (truthy) child Mock, which would
    # silently skip all circuit-breaker bookkeeping. Real callables (like
    # stripe.checkout.Session.create in production) don't have this attribute,
    # so this only matters for tests.
    mock._ignore_on_call = False
    return mock


async def test_breaker_opens_after_repeated_stripe_failures(client, login_as, monkeypatch):
    login_as(PARTICIPANT)
    create_mock = _failing_mock(stripe.APIConnectionError("network down"))
    monkeypatch.setattr("app.service.stripe.checkout.Session.create", create_mock)

    # fail_max=3: the first 2 calls hit Stripe and fail normally (-> 502). The
    # 3rd call also reaches Stripe, but that failure crosses the threshold, so
    # it surfaces as a circuit-breaker 503 instead of a plain Stripe error.
    for registration_id, expected_status in ((1, 502), (2, 502), (3, 503)):
        resp = await client.post(
            "/payments/checkout", json={"registration_id": registration_id, "amount": 25.0}
        )
        assert resp.status_code == expected_status

    assert stripe_checkout_breaker.current_state == CircuitBreakerState.OPEN
    assert create_mock.call_count == 3

    # Now the breaker is open: it should fail fast with 503 and NOT call Stripe again.
    resp = await client.post("/payments/checkout", json={"registration_id": 4, "amount": 25.0})
    assert resp.status_code == 503
    assert create_mock.call_count == 3


async def test_card_decline_does_not_trip_the_breaker(client, login_as, monkeypatch):
    login_as(PARTICIPANT)
    create_mock = _failing_mock(
        stripe.CardError("Your card was declined.", param="card", code="card_declined")
    )
    monkeypatch.setattr("app.service.stripe.checkout.Session.create", create_mock)

    # Card declines are the customer's fault, not Stripe being down, so they're
    # excluded from the breaker's failure count -- even many of them in a row
    # should never open the breaker.
    for registration_id in range(1, 6):
        resp = await client.post(
            "/payments/checkout", json={"registration_id": registration_id, "amount": 25.0}
        )
        assert resp.status_code == 502

    assert stripe_checkout_breaker.current_state == CircuitBreakerState.CLOSED
    assert create_mock.call_count == 5

    # A subsequent, successful checkout should still go through normally.
    monkeypatch.setattr(
        "app.service.stripe.checkout.Session.create",
        Mock(return_value=SimpleNamespace(id="cs_test_ok", url="https://checkout.stripe.com/ok")),
    )
    resp = await client.post("/payments/checkout", json={"registration_id": 6, "amount": 25.0})
    assert resp.status_code == 200
