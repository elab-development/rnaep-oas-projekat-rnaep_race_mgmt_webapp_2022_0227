from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
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

async def create_registration(db: AsyncSession, participant_id: int, race_id: int, track_id: int, data: RegistrationCreate):
    registration = await registration_repository.create_registration(db, participant_id, race_id, track_id, data)
    if not registration:    
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Registration failed. Possible reasons: invalid race or track ID, registration already exists for this participant on the same track, or race registration deadline has passed.")
    return RegistrationResponse.model_validate(registration)

async def delete_registration(db: AsyncSession, registration_id: int, participant_id: int):
    registration = await registration_repository.get_registration_by_id(db, registration_id)
    if not registration:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Registration not found")
    if registration.participant_id != participant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this registration")
    return await registration_repository.delete_registration(db, registration_id)
