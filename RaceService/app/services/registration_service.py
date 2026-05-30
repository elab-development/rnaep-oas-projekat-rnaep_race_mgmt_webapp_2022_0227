from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.db.repositories import race_repository, track_repository
from app.enum import RaceStatusEnum
from app.api.schema import RegistrationCreate, RegistrationResponse, RegistrationResponse
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
    track = await track_repository.get_track_by_id(db, data.track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    race = await race_repository.get_race_by_id(db, track.race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")
    if race.status != RaceStatusEnum.UPCOMING:
        raise HTTPException(status_code=400, detail="Race is not open for registration")
    if datetime.now(timezone.utc) > race.deadline:
        raise HTTPException(status_code=400, detail="Registration deadline has passed") 
    registration = await registration_repository.create_registration(
        db, participant_id, race.id, data.track_id, data
    )
    return RegistrationResponse.model_validate(registration)

async def delete_registration(db: AsyncSession, registration_id: int, participant_id: int):
    registration = await registration_repository.get_registration_by_id(db, registration_id)
    if not registration:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registration not found")
    if registration.participant_id != participant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this registration")
    return await registration_repository.delete_registration(db, registration_id)
