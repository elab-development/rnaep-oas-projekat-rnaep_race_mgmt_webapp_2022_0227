import json
import asyncio
from aiokafka import AIOKafkaProducer
from aiokafka.errors import GroupCoordinatorNotAvailableError, KafkaConnectionError
from app.config import settings
from app.api.schema import PaymentResponse

producer = None

async def start_producer():
    global producer
    producer = AIOKafkaProducer(bootstrap_servers=settings.kafka_bootstrap_servers)
    
    while True:
        try:
            print("Payment Service: Attempting to connect Producer to Kafka...")
            await producer.start()
            print("Payment Service: Producer successfully connected to Kafka!")
            break
        except (KafkaConnectionError, GroupCoordinatorNotAvailableError) as e:
            print(f"Payment Service: Producer backup/retry due to: {e}")
            await asyncio.sleep(3)  

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