from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Depends, status
from app.db.db import get_db
from app import service
from app.api.schema import RaceCreate, RaceResponse



race_router = APIRouter(prefix="/api/race", tags=["Races"])

@race_router.get("/{race_id}", response_model=RaceResponse, status_code=status.HTTP_200_OK)
async def get_race(race_id: int, db: AsyncSession = Depends(get_db)):
    return await service.get_race_by_id(db, race_id)

@race_router.post("/", response_model=RaceResponse, status_code=status.HTTP_201_CREATED)
async def create_race(data: RaceCreate, organiser_id: int, db: AsyncSession = Depends(get_db)):
    return await service.create_race(db, data, organiser_id)