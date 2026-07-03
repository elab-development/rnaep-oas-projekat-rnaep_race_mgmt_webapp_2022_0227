from app.core.auth import create_access_token, hash_password, verify_password, verify_token


def test_hash_password_is_salted():
    first = hash_password("supersecret1")
    second = hash_password("supersecret1")
    assert first != second


def test_verify_password_roundtrip():
    hashed = hash_password("supersecret1")
    assert verify_password("supersecret1", hashed)
    assert not verify_password("wrong-password", hashed)


def test_create_and_verify_access_token_roundtrip():
    token = create_access_token({"sub": "42", "role": "participant"})
    payload = verify_token(token)
    assert payload["sub"] == "42"
    assert payload["role"] == "participant"


def test_verify_token_rejects_garbage():
    assert verify_token("not-a-jwt") is None


def test_verify_token_rejects_tampered_signature():
    token = create_access_token({"sub": "1"})
    tampered = token[:-1] + ("a" if token[-1] != "a" else "b")
    assert verify_token(tampered) is None


def test_verify_token_requires_sub_claim():
    # exp is added automatically by create_access_token, but a token without "sub" must fail.
    from datetime import UTC, datetime, timedelta

    import jwt

    from app.config import settings

    payload = {"exp": datetime.now(UTC) + timedelta(days=1)}
    token = jwt.encode(payload, settings.secret_key.get_secret_value(), algorithm=settings.algorithm)
    assert verify_token(token) is None
