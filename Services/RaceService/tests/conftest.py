import os
from datetime import datetime, timezone
from unittest.mock import AsyncMock

os.environ.setdefault("RACE_DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("USER_SECRET_KEY", "test-secret-key-for-pytest-only-not-for-production-use")
os.environ.setdefault("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
os.environ.setdefault("MAILTRAP_API_TOKEN", "test-mailtrap-token")
os.environ.setdefault("MAILTRAP_SANDBOX", "true")
os.environ.setdefault("EMAIL_FROM", "noreply@example.com")
os.environ.setdefault("EMAIL_SUPPORT", "support@example.com")

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.dialects.sqlite.base import DATETIME as SQLiteDATETime
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.pool import StaticPool
from sqlalchemy.sql.elements import TextClause

from app.core.dependencies import get_current_user
from app.db.db import Base, get_db
from main import app


@compiles(TextClause, "sqlite")
def _sqlite_wrap_now_default(element, compiler, **kw):
    # SQLite's DDL grammar requires function-call defaults to be parenthesized
    # (`DEFAULT (NOW())`), unlike Postgres. Older SQLAlchemy pins emit the bare
    # `text("NOW()")` verbatim, which is valid on Postgres but not on SQLite.
    text = element.text
    return f"({text})" if text.strip().upper() == "NOW()" else text


# SQLite has no tz-aware timestamp storage: DateTime(timezone=True) columns come
# back offset-naive, unlike on Postgres. The app assumes UTC everywhere, so make
# SQLite behave the same way for tests instead of touching production models.
_original_result_processor = SQLiteDATETime.result_processor


def _tz_aware_result_processor(self, dialect, coltype):
    process = _original_result_processor(self, dialect, coltype)

    def process_and_localize(value):
        result = process(value)
        if result is not None and result.tzinfo is None:
            result = result.replace(tzinfo=timezone.utc)
        return result

    return process_and_localize


SQLiteDATETime.result_processor = _tz_aware_result_processor

test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    poolclass=StaticPool,
    connect_args={"check_same_thread": False},
)


@event.listens_for(test_engine.sync_engine, "connect")
def _register_sqlite_now(dbapi_connection, _):
    dbapi_connection.create_function("NOW", 0, lambda: datetime.now(timezone.utc).isoformat())


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
def _no_real_kafka_or_email(monkeypatch):
    # These would otherwise try to reach a real Kafka broker / Mailtrap over the
    # network; the app already swallows failures from them, but without mocking,
    # tests would be slow/flaky and wouldn't let us assert on what was published/sent.
    monkeypatch.setattr(
        "app.services.registration_service.send_registration_created", AsyncMock()
    )
    monkeypatch.setattr(
        "app.services.registration_service.send_registration_deleted", AsyncMock()
    )
    monkeypatch.setattr(
        "app.services.registration_service.send_registration_pending_email", AsyncMock()
    )
    monkeypatch.setattr(
        "app.kafka.consumer.send_registration_confirmed_email", AsyncMock()
    )
    monkeypatch.setattr(
        "app.kafka.consumer.send_registration_failed_email", AsyncMock()
    )


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
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
