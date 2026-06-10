from aiokafka import AIOKafkaConsumer
import json
from app.enum import PaymentStatusEnum
from app.db.repositories import registration_repository
from app.config import settings
from app.db.db import async_session_maker

consumer = None

async def start_consumer():
    global consumer
    consumer = AIOKafkaConsumer(
        "payment_completed", "payment_failed",
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id="race_service_group"
    )
    await consumer.start()
    async for msg in consumer:
        data = json.loads(msg.value.decode('utf-8'))
        if msg.topic == "payment_completed":
            await handle_payment_completed(data)
        elif msg.topic == "payment_failed":
            await handle_payment_failed(data)

async def stop_consumer():
    global consumer
    if consumer:
        await consumer.stop()

async def handle_payment_completed(data: dict):
    async with async_session_maker() as db:
        registration_id = data.get("id")
        await registration_repository.update_registration_payment_status(
            db, registration_id, PaymentStatusEnum.COMPLETED
        )

async def handle_payment_failed(data: dict):
    async with async_session_maker() as db:
        registration_id = data.get("id")
        await registration_repository.update_registration_payment_status(
            db, registration_id, PaymentStatusEnum.FAILED
        )