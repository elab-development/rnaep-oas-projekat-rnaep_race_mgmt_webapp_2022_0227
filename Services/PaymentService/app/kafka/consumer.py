import json
import asyncio
from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaConnectionError, GroupCoordinatorNotAvailableError
from app.api.schema import PaymentCreate
from app.config import settings
from app.db.db import SessionLocal
from app.service import create_checkout_session

async def start_consumer():
    global consumer
    consumer = AIOKafkaConsumer(
        "registration_created",
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
            data = json.loads(msg.value.decode('utf-8'))
            print(f"Payment Service: Accepted message from Kafka -> {data}")
            
            await handle_registration_created(data)
            
            print("Payment Service: Successfully processed registration_created and created Stripe session!")
        except Exception as e:
            print(f"ERROR in Payment Service Consumer-u: {str(e)}")

async def stop_consumer():
    global consumer
    if consumer:
        await consumer.stop()

async def handle_registration_created(data: dict):
    async with SessionLocal() as db:
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