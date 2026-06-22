import asyncio
import json
from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaConnectionError, GroupCoordinatorNotAvailableError
from app.config import settings
from app.db.db import SessionLocal
from app.db.repositories import registration_repository, race_repository
from app.enum import PaymentStatusEnum
from app.services.email_service import send_registration_confirmed_email, send_registration_failed_email


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
            print("Race Service: Attempting to connect Consumer to Kafka...")
            await consumer.start()
            print("Race Service: Consumer successfully connected to Kafka!")
            break
        except (KafkaConnectionError, GroupCoordinatorNotAvailableError) as e:
            print(f"Race Service: Kafka not ready ({e}). Retrying in 3 seconds...")
            await asyncio.sleep(3)

    async for msg in consumer:
        try:
            data = json.loads(msg.value.decode('utf-8'))
            print(f"Race Service: Received message -> {data}")
            if msg.topic == "payment_completed":
                await handle_payment_completed(data)
            elif msg.topic == "payment_failed":
                await handle_payment_failed(data)
        except Exception as e:
            print(f"Race Service Consumer ERROR: {str(e)}")

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
        print(f"Race Service: Registration {data['registration_id']} marked as COMPLETED")

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
            print(
                f"Race Service: Preskoćeno slanje mejla za registraciju "
                f"{data['registration_id']} – email nije prosleđen u Kafka poruci."
            )

async def handle_payment_failed(data: dict):
    async with SessionLocal() as db:
        registration = await registration_repository.update_registration_payment_status(
            db,
            registration_id=data["registration_id"],
            status=PaymentStatusEnum.FAILED,
        )
        print(f"Race Service: Registration {data['registration_id']} marked as FAILED")

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
            print(
                f"Race Service: Preskoćeno slanje mejla za registraciju "
                f"{data['registration_id']} – email nije prosleđen u Kafka poruci."
            )