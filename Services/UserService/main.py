from fastapi import FastAPI
from middleware import validation_error_handler
from app.api.router import auth_router, user_router
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

Instrumentator().instrument(app).expose(app)

validation_error_handler(app)

app.include_router(auth_router)
app.include_router(user_router)

