PARTICIPANT_PAYLOAD = {
    "email": "runner@example.com",
    "first_name": "Ana",
    "last_name": "Anic",
    "password": "password123",
    "date_of_birth": "1995-01-01",
    "gender": "FEMALE",
    "tshirt_size": "M",
    "emergency_contact": "+381601234567",
}

ORGANISER_PAYLOAD = {
    "email": "org@example.com",
    "first_name": "Org",
    "last_name": "Team",
    "password": "password123",
    "organization_name": "Trail Runners",
    "website": None,
    "description": "A community trail running club active since 2010.",
}


async def test_register_participant_success(client):
    resp = await client.post("/api/users/auth/register/participant", json=PARTICIPANT_PAYLOAD)
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == PARTICIPANT_PAYLOAD["email"]
    assert body["participant"]["gender"] == "FEMALE"
    assert body["organiser"] is None


async def test_register_organiser_success(client):
    resp = await client.post("/api/users/auth/register/organiser", json=ORGANISER_PAYLOAD)
    assert resp.status_code == 201
    body = resp.json()
    assert body["organiser"]["organization_name"] == "Trail Runners"
    assert body["participant"] is None


async def test_register_participant_duplicate_email_rejected(client):
    first = await client.post("/api/users/auth/register/participant", json=PARTICIPANT_PAYLOAD)
    assert first.status_code == 201

    second = await client.post("/api/users/auth/register/participant", json=PARTICIPANT_PAYLOAD)
    assert second.status_code == 400


async def test_register_participant_invalid_payload_returns_400(client):
    bad_payload = {**PARTICIPANT_PAYLOAD, "password": "short"}
    resp = await client.post("/api/users/auth/register/participant", json=bad_payload)
    assert resp.status_code == 400
    assert "password" in resp.json()["errors"]


async def test_login_success_sets_httponly_cookie(client):
    await client.post("/api/users/auth/register/participant", json=PARTICIPANT_PAYLOAD)

    resp = await client.post(
        "/api/users/auth/login",
        json={"email": PARTICIPANT_PAYLOAD["email"], "password": PARTICIPANT_PAYLOAD["password"]},
    )
    assert resp.status_code == 200
    assert "access_token" in resp.cookies


async def test_login_wrong_password_rejected(client):
    await client.post("/api/users/auth/register/participant", json=PARTICIPANT_PAYLOAD)

    resp = await client.post(
        "/api/users/auth/login",
        json={"email": PARTICIPANT_PAYLOAD["email"], "password": "wrong-password"},
    )
    assert resp.status_code == 401


async def test_login_unknown_email_rejected(client):
    resp = await client.post(
        "/api/users/auth/login",
        json={"email": "nobody@example.com", "password": "password123"},
    )
    assert resp.status_code == 401


async def test_get_me_without_cookie_is_unauthenticated(client):
    resp = await client.get("/api/users/me")
    assert resp.status_code == 401


async def test_get_me_returns_current_user_after_login(client):
    await client.post("/api/users/auth/register/participant", json=PARTICIPANT_PAYLOAD)
    await client.post(
        "/api/users/auth/login",
        json={"email": PARTICIPANT_PAYLOAD["email"], "password": PARTICIPANT_PAYLOAD["password"]},
    )

    resp = await client.get("/api/users/me")
    assert resp.status_code == 200
    assert resp.json()["email"] == PARTICIPANT_PAYLOAD["email"]


async def test_logout_clears_cookie(client):
    await client.post("/api/users/auth/register/participant", json=PARTICIPANT_PAYLOAD)
    await client.post(
        "/api/users/auth/login",
        json={"email": PARTICIPANT_PAYLOAD["email"], "password": PARTICIPANT_PAYLOAD["password"]},
    )

    resp = await client.post("/api/users/auth/logout")
    assert resp.status_code == 200

    me_resp = await client.get("/api/users/me")
    assert me_resp.status_code == 401
