import json
from aiokafka import AIOKafkaProducer
from app.config import settings
from app.api.schema import RegistrationResponse

producer = None

async def start_producer():
    global producer
    producer = AIOKafkaProducer(bootstrap_servers=settings.kafka_bootstrap_servers)
    await producer.start()

async def stop_producer():
    global producer
    if producer:
        await producer.stop()

async def send_registration_created(registration: RegistrationResponse, amount: float):
    message = registration.model_dump(mode="json")
    message['amount'] = amount
    await producer.send_and_wait(
        "registration_created",
        json.dumps(message).encode('utf-8')
    )