import json
from aiokafka import AIOKafkaProducer
from app.config import settings
from app.api.schema import PaymentResponse, RegistrationResponse

producer = None

async def start_producer():
    global producer
    producer = AIOKafkaProducer(bootstrap_servers=settings.kafka_bootstrap_servers)
    await producer.start()

async def stop_producer():
    global producer
    if producer:
        await producer.stop()

async def send_payment_completed(payment: PaymentResponse):
    message = payment.model_dump(mode="json")
    await producer.send_and_wait(
        "payment_completed",
        json.dumps(message).encode('utf-8')
    )

async def send_payment_failed(payment: PaymentResponse):
    message = payment.model_dump(mode="json")
    await producer.send_and_wait(
        "payment_failed",
        json.dumps(message).encode('utf-8')
    )