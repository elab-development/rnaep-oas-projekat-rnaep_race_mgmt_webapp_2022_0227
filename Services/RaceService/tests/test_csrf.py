from httpx import ASGITransport, AsyncClient

from main import app
from tests.helpers import make_race_payload

ORGANISER = {"sub": "1", "role": "organiser", "email": "org@example.com", "username": "Org One"}


async def test_create_race_rejected_without_csrf_token(login_as):
    login_as(ORGANISER)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post("/api/race/", json=make_race_payload())
    assert resp.status_code == 403


async def test_create_race_rejected_with_mismatched_csrf_token(login_as):
    login_as(ORGANISER)
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        cookies={"csrf_token": "cookie-value"},
        headers={"X-CSRF-Token": "different-header-value"},
    ) as ac:
        resp = await ac.post("/api/race/", json=make_race_payload())
    assert resp.status_code == 403


async def test_create_race_succeeds_with_matching_csrf_token(login_as):
    login_as(ORGANISER)
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://test",
        cookies={"csrf_token": "matching-value"},
        headers={"X-CSRF-Token": "matching-value"},
    ) as ac:
        resp = await ac.post("/api/race/", json=make_race_payload())
    assert resp.status_code == 201


async def test_get_races_does_not_require_csrf_token():
    # GET requests are never CSRF-checked (they're not state-changing).
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/race/")
    assert resp.status_code == 200
