from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.kafka.producer import start_producer, stop_producer
from app.api.routes import race_router, registration_router
from middleware import validation_error_handler

@asynccontextmanager
async def lifespan(app: FastAPI):
    await start_producer()
    yield
    await stop_producer()

app = FastAPI(lifespan=lifespan)

validation_error_handler(app)

app.include_router(race_router)
app.include_router(registration_router)
