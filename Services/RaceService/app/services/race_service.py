from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.api.schema import RaceCreate, RaceResponse, RaceUpdate
from app.db.repositories import race_repository, registration_repository


# Service functions for Race
async def get_race_by_id(db: AsyncSession, race_id: int):
    race = await race_repository.get_race_by_id(db, race_id)
    if not race:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Race not found")
    return RaceResponse.model_validate(race)

async def get_races(db: AsyncSession):
    races = await race_repository.get_races(db)
    if not races:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Races not found")    
    return [RaceResponse.model_validate(race) for race in races]

async def create_race(db: AsyncSession, data: RaceCreate, organiser_id: int):
    race = await race_repository.create_race(db, data, organiser_id)
    return RaceResponse.model_validate(race)

async def patch_race(db: AsyncSession, race_id: int, organiser_id: int, data: RaceUpdate):
    race = await race_repository.get_race_by_id(db, race_id)
    if not race:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Race not found")
    if race.organiser_id != organiser_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this race")
    updated_race = await race_repository.patch_race(db, race_id, data.model_dump(exclude_unset=True))
    return RaceResponse.model_validate(updated_race)

async def delete_race(db: AsyncSession, race_id: int, organiser_id: int):
    race = await race_repository.get_race_by_id(db, race_id)
    if not race:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Race not found")
    if race.organiser_id != organiser_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this race")
    if await registration_repository.get_registration_count_by_race(db,race_id)>0:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can't do that, race has participants!")
    return await race_repository.delete_race(db, race_id)   
