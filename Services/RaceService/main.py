import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.kafka.consumer import start_consumer, stop_consumer
from app.kafka.producer import start_producer, stop_producer
from app.api.routes import race_router, registration_router
from middleware import validation_error_handler

@asynccontextmanager
async def lifespan(app: FastAPI):
    await start_producer()
    consumer_task = asyncio.create_task(start_consumer())
    yield
    await stop_producer()
    consumer_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        pass
    await stop_consumer()

app = FastAPI(lifespan=lifespan)

validation_error_handler(app)

app.include_router(race_router)
app.include_router(registration_router)
