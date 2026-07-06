import logging
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.kafka.producer import send_registration_created, send_registration_deleted
from app.db.repositories import race_repository
from app.enum import RaceStatusEnum, PaymentStatusEnum
from app.api.schema import RegistrationCreate, RegistrationResponse
from app.db.repositories import registration_repository
from app.services.email_service import send_registration_pending_email

logger = logging.getLogger(__name__)


async def get_registrations_by_race_id(db: AsyncSession, race_id, organiser_id):
    race = await race_repository.get_race_by_id(db, race_id)
    if not race:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Race not found")
    if race.organiser_id != organiser_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access registrations for this race")
    return await registration_repository.get_registrations_by_race_id(db, race_id)

async def get_registration_by_id(db: AsyncSession, registration_id: int, participant_id: int):
    registration = await registration_repository.get_registration_by_id(db, registration_id)
    if not registration:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registration not found")
    if registration.participant_id != participant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this registration")
    return RegistrationResponse.model_validate(registration)

async def get_registrations_by_participant_id(db: AsyncSession, participant_id: int):
    registrations = await registration_repository.get_registrations_by_participant_id(db, participant_id)
    return [RegistrationResponse.model_validate(reg) for reg in registrations]

async def create_registration(
    db: AsyncSession,
    participant_id: int,
    data: RegistrationCreate,
    participant_email: str,
    participant_name: str,
):
    race = await race_repository.get_race_by_id(db, data.race_id)
    if not race:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Race not found")
    existing_registration = await registration_repository.get_registration_by_participant_and_race(db, participant_id, data.race_id)
    if existing_registration:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already registered for this race")
    if race.status != RaceStatusEnum.UPCOMING:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Race is not open for registration")
    if datetime.now(timezone.utc) > race.deadline:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Registration deadline has passed")
    count = await registration_repository.get_registration_count_by_race(db, data.race_id)
    if count >= race.max_participants:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Race is full")
    try:
        registration = await registration_repository.create_registration(
            db, participant_id, race.id, data
        )
        response = RegistrationResponse.model_validate(registration)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    try:
        await send_registration_created(
            response, float(race.price),
            participant_email=participant_email, participant_name=participant_name,
        )
    except Exception:
        logger.error("Kafka registration_created publish failed", exc_info=True)

    try:
        await send_registration_pending_email(
            to_email=participant_email, participant_name=participant_name,
            race_name=race.name,
            race_date=race.date_time.strftime("%d.%m.%Y. u %H:%M"),
            race_location=race.location, registration_id=response.id,
        )
    except Exception:
        logger.error("Pending-registration email failed", exc_info=True)
    return response

async def delete_registration(db: AsyncSession, registration_id: int, participant_id: int):
    registration = await registration_repository.get_registration_by_id(db, registration_id)
    if not registration:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registration not found")
    if registration.participant_id != participant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this registration")
    if registration.payment_status == PaymentStatusEnum.COMPLETED:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Registration can't be canceled")
    deleted = await registration_repository.delete_registration(db, registration_id)
    if deleted:
        try:
            await send_registration_deleted(registration_id)
        except Exception:
            logger.error("Kafka registration_deleted publish failed", exc_info=True)
    return deleted