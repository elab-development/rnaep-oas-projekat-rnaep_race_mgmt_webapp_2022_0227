from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Depends, status
from app.db.db import get_db
from app import service
from app.api.schema import RaceCreate, RaceResponse, TrackCreate, TrackResponse, TrackUpdate



race_router = APIRouter(prefix="/api/race", tags=["Races"])

@race_router.get("/{race_id}", response_model=RaceResponse, status_code=status.HTTP_200_OK)
async def get_race(race_id: int, db: AsyncSession = Depends(get_db)):
    return await service.get_race_by_id(db, race_id)

@race_router.post("/", response_model=RaceResponse, status_code=status.HTTP_201_CREATED)
async def create_race(data: RaceCreate, organiser_id: int, db: AsyncSession = Depends(get_db)):
    return await service.create_race(db, data, organiser_id)

@race_router.patch("/{race_id}", response_model=RaceResponse, status_code=status.HTTP_200_OK)
async def update_race(race_id: int, data: RaceCreate, organiser_id: int, db: AsyncSession = Depends(get_db)):
    return await service.patch_race(db, race_id, organiser_id, data)

@race_router.delete("/{race_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_race(race_id: int, organiser_id: int, db: AsyncSession = Depends(get_db)):
    await service.delete_race(db, race_id, organiser_id)


track_router = APIRouter(prefix="/api/track", tags=["Tracks"])

@track_router.get("/{track_id}", response_model=TrackResponse, status_code=status.HTTP_200_OK)
async def get_track(track_id: int, db: AsyncSession = Depends(get_db)):
    return await service.get_track_by_id(db, track_id)

@track_router.patch("/{track_id}", response_model=TrackResponse, status_code=status.HTTP_200_OK)
async def update_track(track_id: int, data: TrackUpdate, organiser_id: int, db: AsyncSession = Depends(get_db)):
    return await service.patch_track(db, track_id, organiser_id, data)
    
@track_router.delete("/{track_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_track(track_id: int, organiser_id: int, db: AsyncSession = Depends(get_db)):
    await service.delete_track(db, track_id, organiser_id)

@track_router.post("/add", response_model=TrackResponse, status_code=status.HTTP_201_CREATED)
async def add_track_to_race(race_id: int, data: TrackCreate, organiser_id: int, db: AsyncSession = Depends(get_db)):
    return await service.add_track_to_race(db, race_id, organiser_id, data)