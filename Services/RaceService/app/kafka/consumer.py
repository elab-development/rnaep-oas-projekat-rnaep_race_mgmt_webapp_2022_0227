import asyncio
import json
import logging
from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaConnectionError, GroupCoordinatorNotAvailableError
from app.config import settings
from app.db.db import SessionLocal
from app.db.repositories import registration_repository, race_repository
from app.enum import PaymentStatusEnum
from app.services.email_service import send_registration_confirmed_email, send_registration_failed_email

logger = logging.getLogger(__name__)

consumer = None

async def start_consumer():
    global consumer
    consumer = AIOKafkaConsumer(
        "payment_completed",
        "payment_failed",
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id="race_service_group"
    )

    while True:
        try:
            logger.info("Attempting to connect Consumer to Kafka...")
            await consumer.start()
            logger.info("Consumer successfully connected to Kafka!")
            break
        except (KafkaConnectionError, GroupCoordinatorNotAvailableError) as e:
            logger.warning("Kafka not ready (%s). Retrying in 3 seconds...", e)
            await asyncio.sleep(3)

    async for msg in consumer:
        try:
            data = json.loads(msg.value.decode('utf-8'))
            logger.info("Received message -> %s", data)
            if msg.topic == "payment_completed":
                await handle_payment_completed(data)
            elif msg.topic == "payment_failed":
                await handle_payment_failed(data)
        except Exception:
            logger.error("Consumer error while processing message", exc_info=True)

async def stop_consumer():
    global consumer
    if consumer:
        await consumer.stop()

async def handle_payment_completed(data: dict):
    async with SessionLocal() as db:
        registration = await registration_repository.update_registration_payment_status(
            db,
            registration_id=data["registration_id"],
            status=PaymentStatusEnum.COMPLETED,
        )
        logger.info("Registration %s marked as COMPLETED", data["registration_id"])

        if not registration:
            return

        race = await race_repository.get_race_by_id(db, registration.race_id)

        participant_email = data.get("participant_email")
        participant_name = data.get("participant_name")

        if participant_email and race:
            await send_registration_confirmed_email(
                to_email=participant_email,
                participant_name=participant_name,
                race_name=race.name,
                race_date=race.date_time.strftime("%d.%m.%Y. u %H:%M"),
                race_location=race.location,
                registration_id=registration.id,
                bib_number=registration.bib_number,
            )
        else:
            logger.info(
                "Skipped confirmation email for registration %s - no participant email in Kafka message.",
                data["registration_id"],
            )

async def handle_payment_failed(data: dict):
    async with SessionLocal() as db:
        registration = await registration_repository.update_registration_payment_status(
            db,
            registration_id=data["registration_id"],
            status=PaymentStatusEnum.FAILED,
        )
        logger.info("Registration %s marked as FAILED", data["registration_id"])

        if not registration:
            return

        race = await race_repository.get_race_by_id(db, registration.race_id)

        participant_email = data.get("participant_email")
        participant_name = data.get("participant_name", "Učesniče")

        if participant_email and race:
            await send_registration_failed_email(
                to_email=participant_email,
                participant_name=participant_name,
                race_name=race.name,
                registration_id=registration.id,
            )
        else:
            logger.info(
                "Skipped failure email for registration %s - no participant email in Kafka message.",
                data["registration_id"],
            )