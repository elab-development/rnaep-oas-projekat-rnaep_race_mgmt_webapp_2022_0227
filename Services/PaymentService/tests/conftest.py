import os
from unittest.mock import AsyncMock

os.environ.setdefault("PAYMENT_DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("USER_SECRET_KEY", "test-secret-key-for-pytest-only-not-for-production-use")
os.environ.setdefault("PAYMENT_SECRET_KEY", "sk_test_dummy")
os.environ.setdefault("PAYMENT_WEBHOOK_SECRET", "whsec_test_dummy")
os.environ.setdefault("PAYMENT_SUCCESS_URL", "http://localhost:5173/payments/success")
os.environ.setdefault("PAYMENT_CANCEL_URL", "http://localhost:5173/payments/cancel")
os.environ.setdefault("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.dependencies import get_current_user
from app.db.db import Base, get_db
from main import app

test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    poolclass=StaticPool,
    connect_args={"check_same_thread": False},
)

TestSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False)


async def _override_get_db():
    async with TestSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = _override_get_db


@pytest_asyncio.fixture(autouse=True)
async def _reset_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(autouse=True)
def _no_real_kafka(monkeypatch):
    # app.service imports these directly from app.kafka.producer; patch the bound
    # names in app.service so tests don't try to reach a real Kafka broker.
    monkeypatch.setattr("app.service.send_payment_completed", AsyncMock())
    monkeypatch.setattr("app.service.send_payment_failed", AsyncMock())


@pytest.fixture(autouse=True)
def _reset_circuit_breaker():
    # stripe_checkout_breaker is a module-level singleton; without resetting it,
    # a test that trips it would leave it open for every test that runs after.
    from app.service import stripe_checkout_breaker

    stripe_checkout_breaker.close()
    yield
    stripe_checkout_breaker.close()


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    # Every mutating route now requires a matching csrf_token cookie + X-CSRF-Token
    # header (double-submit CSRF check); use the same fixed value for both so all
    # tests satisfy it by default. /payments/webhook is exempt (Stripe calls it
    # server-to-server, with no browser cookies involved).
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        cookies={"csrf_token": "test-csrf-token"},
        headers={"X-CSRF-Token": "test-csrf-token"},
    ) as ac:
        yield ac


@pytest.fixture
def login_as():
    def _login_as(payload: dict | None):
        if payload is None:
            app.dependency_overrides.pop(get_current_user, None)
        else:
            app.dependency_overrides[get_current_user] = lambda: payload

    yield _login_as
    app.dependency_overrides.pop(get_current_user, None)
