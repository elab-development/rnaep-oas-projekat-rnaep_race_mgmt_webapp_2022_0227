from httpx import ASGITransport, AsyncClient

from main import app

PARTICIPANT_PAYLOAD = {
    "email": "csrf@example.com",
    "first_name": "Csrf",
    "last_name": "Tester",
    "password": "password123",
    "date_of_birth": "1995-01-01",
    "gender": "FEMALE",
    "tshirt_size": "M",
    "emergency_contact": "+381601234567",
}


async def test_register_and_login_do_not_require_csrf_token():
    # Register/login are the auth entry points: no session exists yet, so
    # there's nothing for a forged cross-site request to piggyback on.
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        register_resp = await ac.post("/api/users/auth/register/participant", json=PARTICIPANT_PAYLOAD)
        assert register_resp.status_code == 201

        login_resp = await ac.post(
            "/api/users/auth/login",
            json={"email": PARTICIPANT_PAYLOAD["email"], "password": PARTICIPANT_PAYLOAD["password"]},
        )
        assert login_resp.status_code == 200
        assert "csrf_token" in login_resp.cookies


async def test_logout_rejected_without_csrf_token():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        await ac.post("/api/users/auth/register/participant", json=PARTICIPANT_PAYLOAD)
        await ac.post(
            "/api/users/auth/login",
            json={"email": PARTICIPANT_PAYLOAD["email"], "password": PARTICIPANT_PAYLOAD["password"]},
        )
        resp = await ac.post("/api/users/auth/logout")
        assert resp.status_code == 403


async def test_logout_rejected_with_mismatched_csrf_token():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        await ac.post("/api/users/auth/register/participant", json=PARTICIPANT_PAYLOAD)
        await ac.post(
            "/api/users/auth/login",
            json={"email": PARTICIPANT_PAYLOAD["email"], "password": PARTICIPANT_PAYLOAD["password"]},
        )
        resp = await ac.post(
            "/api/users/auth/logout", headers={"X-CSRF-Token": "not-the-real-token"}
        )
        assert resp.status_code == 403


async def test_logout_succeeds_with_matching_csrf_token():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        await ac.post("/api/users/auth/register/participant", json=PARTICIPANT_PAYLOAD)
        await ac.post(
            "/api/users/auth/login",
            json={"email": PARTICIPANT_PAYLOAD["email"], "password": PARTICIPANT_PAYLOAD["password"]},
        )
        csrf_token = ac.cookies.get("csrf_token")
        resp = await ac.post("/api/users/auth/logout", headers={"X-CSRF-Token": csrf_token})
        assert resp.status_code == 200
