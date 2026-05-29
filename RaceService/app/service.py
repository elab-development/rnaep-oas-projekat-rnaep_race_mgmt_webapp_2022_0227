from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.api.schema import RaceCreate, RaceResponse
from app.db import repository

async def get_race_by_id(db: AsyncSession, race_id: int):
    race = await repository.get_race_by_id(db, race_id)
    if not race:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Race not found")
    return RaceResponse.model_validate(race)

async def create_race(db: AsyncSession, data: RaceCreate, organiser_id: int):
    race = await repository.create_race(db, data, organiser_id)
    return RaceResponse.model_validate(race)
