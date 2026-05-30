from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, status
from app.db.db import get_db
from app.services import track_service
from app.api.schema import TrackResponse, TrackResponse, TrackUpdate, TrackCreate


track_router = APIRouter(prefix="/api/track", tags=["Tracks"])

@track_router.get("/{track_id}", response_model=TrackResponse, status_code=status.HTTP_200_OK)
async def get_track(track_id: int, db: AsyncSession = Depends(get_db)):
    return await track_service.get_track_by_id(db, track_id)

@track_router.patch("/{track_id}", response_model=TrackResponse, status_code=status.HTTP_200_OK)
async def update_track(track_id: int, data: TrackUpdate, organiser_id: int, db: AsyncSession = Depends(get_db)):
    return await track_service.patch_track(db, track_id, organiser_id, data)

@track_router.delete("/{track_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_track(track_id: int, organiser_id: int, db: AsyncSession = Depends(get_db)):
    await track_service.delete_track(db, track_id, organiser_id)

@track_router.post("/{race_id}/tracks", response_model=TrackResponse, status_code=status.HTTP_201_CREATED)
async def add_track_to_race(race_id: int, data: TrackCreate, organiser_id: int, db: AsyncSession = Depends(get_db)):
    return await track_service.add_track_to_race(db, race_id, organiser_id, data)
