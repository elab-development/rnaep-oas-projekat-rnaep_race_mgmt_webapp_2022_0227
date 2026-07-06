from fastapi import FastAPI
from middleware import validation_error_handler, add_security_middleware, add_csrf_protection
from app.api.router import auth_router, user_router
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

Instrumentator().instrument(app).expose(app)

validation_error_handler(app)
add_security_middleware(app)
add_csrf_protection(app, exempt_paths=frozenset({
    "/api/users/auth/register/participant",
    "/api/users/auth/register/organiser",
    "/api/users/auth/login",
}))

app.include_router(auth_router)
app.include_router(user_router)

