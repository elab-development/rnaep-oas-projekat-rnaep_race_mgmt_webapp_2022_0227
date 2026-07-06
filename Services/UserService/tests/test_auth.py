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
    # Flip a character a few positions in from the end, not the very last one:
    # base64url's final character can carry unused padding bits that some
    # decoders ignore, so tampering only the last symbol is occasionally a
    # no-op on the decoded bytes and makes this assertion flaky.
    index = -10
    flipped = "a" if token[index] != "a" else "b"
    tampered = token[:index] + flipped + token[index + 1 :]
    assert verify_token(tampered) is None


def test_verify_token_requires_sub_claim():
    # exp is added automatically by create_access_token, but a token without "sub" must fail.
    from datetime import UTC, datetime, timedelta

    import jwt

    from app.config import settings

    payload = {"exp": datetime.now(UTC) + timedelta(days=1)}
    token = jwt.encode(payload, settings.secret_key.get_secret_value(), algorithm=settings.algorithm)
    assert verify_token(token) is None
