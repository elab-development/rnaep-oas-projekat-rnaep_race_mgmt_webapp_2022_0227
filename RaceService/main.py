from fastapi import FastAPI
from app.api.router import race_router
from middleware import validation_error_handler

app = FastAPI()

validation_error_handler(app)

app.include_router(race_router)


