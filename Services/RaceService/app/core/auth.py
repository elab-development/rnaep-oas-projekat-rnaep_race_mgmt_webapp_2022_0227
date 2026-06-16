import jwt
from fastapi import Cookie, HTTPException, status, Request
from app.config import settings

def verify_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(
            token,
            settings.secret_key.get_secret_value(),
            algorithms=[settings.algorithm],
            options={"require": ["exp", "sub"]}
        )
        return payload 
    except jwt.InvalidTokenError:
        return None