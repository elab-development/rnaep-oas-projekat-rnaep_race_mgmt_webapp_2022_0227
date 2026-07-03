import json
import asyncio
import logging
from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaConnectionError, GroupCoordinatorNotAvailableError
from app.config import settings
from app.db.db import SessionLocal
from app.service import create_checkout_session, delete_payment_by_registration_id

logger = logging.getLogger(__name__)

consumer = None


async def start_consumer():
    global consumer
    consumer = AIOKafkaConsumer(
        "registration_created",
        "registration_deleted",
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id="payment_service_group"
    )

    while True:
        try:
            logger.info("Attempting to connect Consumer to Kafka...")
            await consumer.start()
            logger.info("Consumer successfully connected to Kafka!")
            break
        except (KafkaConnectionError, GroupCoordinatorNotAvailableError) as e:
            logger.warning("Kafka is not ready (%s). Retrying in 3 seconds...", e)
            await asyncio.sleep(3)

    async for msg in consumer:
        try:
            data = json.loads(msg.value.decode("utf-8"))
            logger.info("Accepted message from Kafka -> %s", data)
            if msg.topic == "registration_created":
                await handle_registration_created(data)
            elif msg.topic == "registration_deleted":
                await handle_registration_deleted(data)
        except Exception:
            logger.error("Consumer error while processing message", exc_info=True)


async def stop_consumer():
    global consumer
    if consumer:
        await consumer.stop()


async def handle_registration_created(data: dict):
    async with SessionLocal() as db:
        await create_checkout_session(
            db=db,
            user_id=data["participant_id"],
            registration_id=data["id"],
            amount=data["amount"],
            participant_email=data["participant_email"],
            participant_name=data["participant_name"],
        )


async def handle_registration_deleted(data: dict):
    async with SessionLocal() as db:
        await delete_payment_by_registration_id(db, data["registration_id"])