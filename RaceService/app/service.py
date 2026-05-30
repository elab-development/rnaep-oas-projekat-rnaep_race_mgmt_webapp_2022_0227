from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.api.schema import RaceCreate, RaceResponse, TrackCreate, TrackResponse, TrackUpdate, UpdateRace
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

#Service function for Track

async def get_track_by_id(db: AsyncSession, track_id: int):
    track = await repository.get_track_by_id(db, track_id)
    if not track:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Track not found")
    return TrackResponse.model_validate(track)

async def patch_track(db: AsyncSession, track_id: int, organiser_id: int, data: TrackUpdate):
    track = await repository.get_track_by_id(db, track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    
    race = await repository.get_race_by_id(db, track.race_id)
    if race.organiser_id != organiser_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this track")
    
    updated_track = await repository.patch_track(db, track_id, data.model_dump(exclude_unset=True))
    return TrackResponse.model_validate(updated_track)

async def delete_track(db: AsyncSession, track_id: int, organiser_id: int):
    track = await repository.get_track_by_id(db, track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    
    race = await repository.get_race_by_id(db, track.race_id)
    if race.organiser_id != organiser_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this track")
    
    return await repository.delete_track(db, track_id)

async def add_track_to_race(db: AsyncSession, race_id: int, organiser_id: int, data: TrackCreate):
    race = await repository.get_race_by_id(db, race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")
    if race.organiser_id != organiser_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    track = await repository.add_track_to_race(db, race_id, data.model_dump())
    return TrackResponse.model_validate(track)

#