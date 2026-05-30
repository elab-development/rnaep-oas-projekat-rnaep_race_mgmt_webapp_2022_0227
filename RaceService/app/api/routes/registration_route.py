from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, status
from app.db.db import get_db
from app.services import registration_service
from app.api.schema import RegistrationCreate, RegistrationResponse

registration_router = APIRouter(prefix="/api/registration", tags=["Registrations"])

@registration_router.get("/{registration_id}", response_model=RegistrationResponse, status_code=status.HTTP_200_OK)
async def get_registration(registration_id: int, db: AsyncSession = Depends(get_db)):
    return await registration_service.get_registration_by_id(db, registration_id)  

@registration_router.get("/{participant_id}/participant", response_model=List[RegistrationResponse], status_code=status.HTTP_200_OK)
async def get_registrations_by_participant_id(participant_id: int, db: AsyncSession = Depends(get_db)):
    return await registration_service.get_registrations_by_participant_id(db, participant_id)

@registration_router.post("/", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED)
async def create_registration(data: RegistrationCreate, participant_id: int, db: AsyncSession = Depends(get_db)):
    return await registration_service.create_registration(db, participant_id, data)

@registration_router.delete("/{registration_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_registration(registration_id: int, participant_id: int, db: AsyncSession = Depends(get_db)):
    await registration_service.delete_registration(db, registration_id, participant_id)

    