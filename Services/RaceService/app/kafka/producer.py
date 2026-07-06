import asyncio
import json
import logging
from aiokafka import AIOKafkaProducer
from aiokafka.errors import GroupCoordinatorNotAvailableError, KafkaConnectionError
from app.config import settings
from app.api.schema import RegistrationResponse

logger = logging.getLogger(__name__)

producer = None

async def start_producer():
    global producer
    producer = AIOKafkaProducer(bootstrap_servers=settings.kafka_bootstrap_servers)
    while True:
        try:
            logger.info("Attempting to connect Producer to Kafka...")
            await producer.start()
            logger.info("Producer successfully connected to Kafka!")
            break
        except (KafkaConnectionError, GroupCoordinatorNotAvailableError) as e:
            logger.warning("Producer backoff/retry due to: %s", e)
            await asyncio.sleep(3)

async def stop_producer():
    global producer
    if producer:
        await producer.stop()

async def send_registration_created(
    registration: RegistrationResponse,
    amount: float,
    participant_email: str,
    participant_name: str,
):
    message = registration.model_dump(mode="json")
    message["amount"] = amount
    message["participant_email"] = participant_email
    message["participant_name"] = participant_name
    await producer.send_and_wait(
        "registration_created",
        json.dumps(message).encode("utf-8")
    )

async def send_registration_deleted(registration_id: int):
    message = {"registration_id": registration_id}
    await producer.send_and_wait(
        "registration_deleted",
        json.dumps(message).encode("utf-8")
    )