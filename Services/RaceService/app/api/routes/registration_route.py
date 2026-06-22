from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, status
from app.core.dependencies import get_current_user, require_participant, require_organiser
from app.db.db import get_db
from app.services import registration_service
from app.api.schema import RegistrationCreate, RegistrationResponse

registration_router = APIRouter(prefix="/api/registration", tags=["Registrations"])

@registration_router.get("/", response_model=List[RegistrationResponse], status_code=status.HTTP_200_OK)
async def get_registrations_by_race_id(race_id:int, db: AsyncSession = Depends(get_db), current_user: dict = Depends(require_organiser)):
    organiser_id = int(current_user["sub"])
    return await registration_service.get_registrations_by_race_id(db,race_id,organiser_id)
@registration_router.get("/myregistrations", response_model=List[RegistrationResponse], status_code=status.HTTP_200_OK)
async def get_my_registrations(db: AsyncSession = Depends(get_db), current_user: dict = Depends(require_participant)):
    participant_id = int(current_user["sub"])
    return await registration_service.get_registrations_by_participant_id(db, participant_id)

@registration_router.post("/", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED)
async def create_registration(data: RegistrationCreate, db: AsyncSession = Depends(get_db), current_user: dict = Depends(require_participant)):
    participant_id = int(current_user["sub"])
    return await registration_service.create_registration(db, participant_id, data)

@registration_router.delete("/{registration_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_registration(registration_id: int, db: AsyncSession = Depends(get_db), current_user: dict = Depends(require_participant)):
    participant_id = int(current_user["sub"])
    await registration_service.delete_registration(db, registration_id, participant_id)

    