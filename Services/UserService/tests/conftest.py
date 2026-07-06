import os
from datetime import datetime, timezone

os.environ.setdefault("USER_DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("USER_SECRET_KEY", "test-secret-key-for-pytest-only-not-for-production-use")
os.environ.setdefault("USER_ALGORITHM", "HS256")
os.environ.setdefault("ENVIRONMENT", "test")

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.db.db import Base, get_db
from main import app

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


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    # Every mutating route now requires a matching csrf_token cookie + X-CSRF-Token
    # header (double-submit CSRF check); use the same fixed value for both so all
    # tests satisfy it by default without needing to log in first.
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        cookies={"csrf_token": "test-csrf-token"},
        headers={"X-CSRF-Token": "test-csrf-token"},
    ) as ac:
        yield ac
