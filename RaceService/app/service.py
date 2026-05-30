from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.api.schema import RaceCreate, RaceResponse, UpdateRace
from app.db import repository


# Service functions for Race
async def get_race_by_id(db: AsyncSession, race_id: int):
    race = await repository.get_race_by_id(db, race_id)
    if not race:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Race not found")
    return RaceResponse.model_validate(race)

async def create_race(db: AsyncSession, data: RaceCreate, organiser_id: int):
    race = await repository.create_race(db, data, organiser_id)
    return RaceResponse.model_validate(race)

async def patch_race(db: AsyncSession, race_id: int, organiser_id: int, data: UpdateRace):
    race = await repository.get_race_by_id(db, race_id)
    if not race:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Race not found")
    if race.organiser_id != organiser_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this race")
    updated_race = await repository.patch_race(db, race_id, data.model_dump(exclude_unset=True))
    return RaceResponse.model_validate(updated_race)

async def delete_race(db: AsyncSession, race_id: int, organiser_id: int):
    race = await repository.get_race_by_id(db, race_id)
    if not race:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Race not found")
    if race.organiser_id != organiser_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this race")
    return await repository.delete_race(db, race_id)   