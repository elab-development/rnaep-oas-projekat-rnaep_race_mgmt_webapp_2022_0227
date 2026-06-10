import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.kafka.consumer import start_consumer, stop_consumer
from app.kafka.producer import start_producer, stop_producer
from Services.RaceService.app.kafka.producer import stop_producer
from app.api import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await start_producer()
    asyncio.create_task(start_consumer())
    yield
    await stop_producer()
    await stop_consumer()

app = FastAPI(lifespan=lifespan)

app.include_router(router.router)