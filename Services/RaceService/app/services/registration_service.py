from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.kafka.producer import send_registration_created
from app.db.repositories import race_repository
from app.enum import RaceStatusEnum
from app.api.schema import RegistrationCreate, RegistrationResponse
from app.db.repositories import registration_repository  
#Registration service

async def get_registration_by_id(db: AsyncSession, registration_id: int):
    registration = await registration_repository.get_registration_by_id(db, registration_id)
    if not registration:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registration not found")
    return RegistrationResponse.model_validate(registration)

async def get_registrations_by_participant_id(db: AsyncSession, participant_id: int):
    registrations = await registration_repository.get_registrations_by_participant_id(db, participant_id)
    return [RegistrationResponse.model_validate(reg) for reg in registrations]

async def create_registration(db: AsyncSession, participant_id: int, data: RegistrationCreate):
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
        await send_registration_created(response, float(race.price))
        await db.commit()
        return response
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

async def delete_registration(db: AsyncSession, registration_id: int, participant_id: int):
    registration = await registration_repository.get_registration_by_id(db, registration_id)
    if not registration:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registration not found")
    if registration.participant_id != participant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this registration")
    return await registration_repository.delete_registration(db, registration_id)
