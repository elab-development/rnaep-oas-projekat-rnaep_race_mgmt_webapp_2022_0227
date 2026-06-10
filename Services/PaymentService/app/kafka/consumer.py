from aiokafka import AIOKafkaConsumer
import json
from app.api.schema import PaymentCreate
from app.config import settings
from app.db.db import async_session_maker
from app.service import create_checkout_session

async def start_consumer():
    global consumer
    consumer = AIOKafkaConsumer(
        "registration_created",
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id="payment_service_group"
    )
    await consumer.start()
    async for msg in consumer:
        data = json.loads(msg.value.decode('utf-8'))
        await handle_registration_created(data)

async def stop_consumer():
    global consumer
    if consumer:
        await consumer.stop()

async def handle_registration_created(data: dict):
    async with async_session_maker() as db:
        payment_data = PaymentCreate(
            registration_id=data["id"],
            amount=data["amount"]
        )
        await create_checkout_session(
            db=db,
            user_id=data["participant_id"],
            registration_id=payment_data.registration_id,
            amount=payment_data.amount
        )