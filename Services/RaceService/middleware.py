import secrets

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

CSRF_UNSAFE_METHODS = ("POST", "PUT", "PATCH", "DELETE")

def add_security_middleware(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE"],
        allow_headers=["Content-Type", "Accept", "X-CSRF-Token"],
    )

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        response = await call_next(request)
        if request.url.path not in ("/docs", "/redoc", "/openapi.json"):
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response


def add_csrf_protection(app: FastAPI, exempt_paths: frozenset[str] = frozenset()):
    """Double-submit cookie CSRF check for state-changing requests.

    The `csrf_token` cookie is set (non-httpOnly) by UserService at login. A
    cross-site attacker page can't read it due to the same-origin policy, so
    it can't reproduce it in the X-CSRF-Token header even though the browser
    will still attach the auth cookie automatically.
    """
    @app.middleware("http")
    async def csrf_protection(request: Request, call_next):
        if request.method in CSRF_UNSAFE_METHODS and request.url.path not in exempt_paths:
            cookie_token = request.cookies.get("csrf_token")
            header_token = request.headers.get("x-csrf-token")
            if not cookie_token or not header_token or not secrets.compare_digest(cookie_token, header_token):
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "Missing or invalid CSRF token"},
                )
        return await call_next(request)

def validation_error_handler(app: FastAPI):
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = {}
        for error in exc.errors():
            field_name = error['loc'][-1]
            message = error['msg'].replace("Value error, ", "")
            errors[field_name] = message
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "detail": "Validation error",
                "errors": errors
            }
        )