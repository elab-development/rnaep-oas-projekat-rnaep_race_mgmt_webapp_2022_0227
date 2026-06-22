import json
import asyncio
from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaConnectionError, GroupCoordinatorNotAvailableError
from app.config import settings
from app.db.db import SessionLocal
from app.service import create_checkout_session, delete_payment_by_registration_id

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
            print("Payment Service: Attempting to connect Consumer to Kafka...")
            await consumer.start()
            print("Payment Service: Consumer successfully connected to Kafka!")
            break
        except (KafkaConnectionError, GroupCoordinatorNotAvailableError) as e:
            print(f"Payment Service: Kafka is not ready ({e}). Retrying in 3 seconds...")
            await asyncio.sleep(3)

    async for msg in consumer:
        try:
            data = json.loads(msg.value.decode("utf-8"))
            print(f"Payment Service: Accepted message from Kafka -> {data}")
            if msg.topic == "registration_created":
                await handle_registration_created(data)
            elif msg.topic == "registration_deleted":
                await handle_registration_deleted(data)
        except Exception as e:
            print(f"ERROR in Payment Service Consumer: {str(e)}")


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
    await db.commit()



async def handle_registration_deleted(data: dict):
    async with SessionLocal() as db:
        await delete_payment_by_registration_id(db, data["registration_id"])
    await db.commit()