import asyncio

from aiokafka import AIOKafkaConsumer
from aiokafka.errors import GroupCoordinatorNotAvailableError, KafkaConnectionError
import json
from app.enum import PaymentStatusEnum
from app.db.repositories import registration_repository
from app.config import settings
from app.db.db import SessionLocal

consumer = None

async def start_consumer():
    global consumer
    consumer = AIOKafkaConsumer(
        "payment_completed", "payment_failed",
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id="race_service_group"
    )
    while True:
        try:
            print("Race Service: Attempting to connect Consumer to Kafka...")
            await consumer.start()
            print("Race Service: Consumer successfully connected to Kafka!")
            break
        except (KafkaConnectionError, GroupCoordinatorNotAvailableError) as e:
            print(f"Race Service: Kafka is not ready ({e}). Retrying in 3 seconds...")
            await asyncio.sleep(3)
        async for msg in consumer:
            try:
                data = json.loads(msg.value.decode('utf-8'))
                print(f"Race Service: Accepted message from topic '{msg.topic}' -> {data}")
                
                if msg.topic == "payment_completed":
                    await handle_payment_completed(data)
                    print(f"Race Service: Successfully processed payment_completed for registration ID: {data.get('id')}")
                elif msg.topic == "payment_failed":
                    await handle_payment_failed(data)
                    print(f"Race Service: Successfully processed payment_failed for registration ID: {data.get('id')}")
                    
            except Exception as e:
                print(f"ERROR in Race Service Consumer for topic '{msg.topic}': {str(e)}")

async def stop_consumer():
    global consumer
    if consumer:
        await consumer.stop()

async def handle_payment_completed(data: dict):
    async with SessionLocal() as db:
        registration_id = data.get("id")
        await registration_repository.update_registration_payment_status(
            db, registration_id, PaymentStatusEnum.COMPLETED
        )

async def handle_payment_failed(data: dict):
    async with SessionLocal() as db:
        registration_id = data.get("id")
        await registration_repository.update_registration_payment_status(
            db, registration_id, PaymentStatusEnum.FAILED
        )