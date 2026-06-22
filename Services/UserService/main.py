from fastapi import FastAPI
from middleware import validation_error_handler, add_security_middleware
from app.api.router import auth_router, user_router
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

Instrumentator().instrument(app).expose(app)

validation_error_handler(app)
add_security_middleware(app)

app.include_router(auth_router)
app.include_router(user_router)

