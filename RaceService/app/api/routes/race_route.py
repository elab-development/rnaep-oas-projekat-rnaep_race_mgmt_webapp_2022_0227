from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, status
from app.db.db import get_db
from app.services import race_service
from app.api.schema import RaceCreate, RaceResponse, RaceUpdate

race_router = APIRouter(prefix="/api/race", tags=["Races"])

@race_router.get("/{race_id}", response_model=RaceResponse, status_code=status.HTTP_200_OK)
async def get_race(race_id: int, db: AsyncSession = Depends(get_db)):
    return await race_service.get_race_by_id(db, race_id)

@race_router.post("/", response_model=RaceResponse, status_code=status.HTTP_201_CREATED)
async def create_race(data: RaceCreate, organiser_id: int, db: AsyncSession = Depends(get_db)):
    return await race_service.create_race(db, data, organiser_id)

@race_router.patch("/{race_id}", response_model=RaceResponse, status_code=status.HTTP_200_OK)
async def update_race(race_id: int, data: RaceUpdate, organiser_id: int, db: AsyncSession = Depends(get_db)):
    return await race_service.patch_race(db, race_id, organiser_id, data)

@race_router.delete("/{race_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_race(race_id: int, organiser_id: int, db: AsyncSession = Depends(get_db)):
    await race_service.delete_race(db, race_id, organiser_id)    