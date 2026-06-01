from fastapi import FastAPI
from app.api.routes import race_router, registration_router
from middleware import validation_error_handler

app = FastAPI()

validation_error_handler(app)

app.include_router(race_router)
app.include_router(registration_router)
