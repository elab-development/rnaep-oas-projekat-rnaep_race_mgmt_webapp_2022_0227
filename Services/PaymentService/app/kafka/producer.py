import json
import asyncio
import logging
from aiokafka import AIOKafkaProducer
from aiokafka.errors import GroupCoordinatorNotAvailableError, KafkaConnectionError
from app.config import settings
from app.api.schema import PaymentResponse

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

async def send_payment_completed(payment: PaymentResponse, participant_email: str, participant_name: str):
    message = payment.model_dump(mode="json")
    message["participant_email"] = participant_email
    message["participant_name"] = participant_name
    await producer.send_and_wait("payment_completed", json.dumps(message).encode('utf-8'))

async def send_payment_failed(payment: PaymentResponse, participant_email: str, participant_name: str):
    message = payment.model_dump(mode="json")
    message["participant_email"] = participant_email
    message["participant_name"] = participant_name
    await producer.send_and_wait("payment_failed", json.dumps(message).encode('utf-8'))