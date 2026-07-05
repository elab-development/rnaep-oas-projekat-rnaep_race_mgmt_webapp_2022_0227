import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.logging_config import configure_logging
from app.kafka.consumer import start_consumer, stop_consumer
from app.kafka.producer import start_producer, stop_producer
from app.api import router
from prometheus_fastapi_instrumentator import Instrumentator
from middleware import add_security_middleware, add_csrf_protection

configure_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await start_producer()
    consumer_task = asyncio.create_task(start_consumer())
    yield
    await stop_consumer()
    consumer_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        pass
    await stop_producer()

app = FastAPI(lifespan=lifespan)

add_security_middleware(app)
add_csrf_protection(app, exempt_paths=frozenset({"/payments/webhook"}))

Instrumentator().instrument(app).expose(app)

app.include_router(router.router)