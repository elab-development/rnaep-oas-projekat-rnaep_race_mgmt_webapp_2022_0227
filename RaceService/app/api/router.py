from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Depends, status
from app.db.db import get_db
from app import service
from app.api.schema import CreateObstacle, ObstacleResponse, ObstacleUpdate, RaceCreate, RaceResponse, RegistrationCreate, RegistrationResponse, TrackCreate, TrackObstacleCreate, TrackResponse, TrackUpdate



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

obstacle_router = APIRouter(prefix="/api/obstacle", tags=["Obstacles"])

@obstacle_router.get("/{obstacle_id}", response_model=ObstacleResponse, status_code=status.HTTP_200_OK)
async def get_obstacle(obstacle_id: int, db: AsyncSession = Depends(get_db)):
    return await service.get_obstacle_by_id(db, obstacle_id)

@obstacle_router.post("/", response_model=ObstacleResponse, status_code=status.HTTP_201_CREATED)
async def create_obstacle(data: CreateObstacle, organiser_id: int, db: AsyncSession = Depends(get_db)):
    return await service.add_obstacle(db, data, organiser_id)   

@obstacle_router.patch("/{obstacle_id}", response_model=ObstacleResponse, status_code=status.HTTP_200_OK)
async def update_obstacle(obstacle_id: int, data: ObstacleUpdate, organiser_id: int, db: AsyncSession = Depends(get_db)):
    return await service.patch_obstacle(db, obstacle_id, data, organiser_id)

@obstacle_router.post("/map", status_code=status.HTTP_200_OK)
async def map_obstacle_to_track(track_id: int, obstacle_id: int, data: TrackObstacleCreate, organiser_id: int, db: AsyncSession = Depends(get_db)):
    return await service.map_obstacle_to_track(db, track_id, obstacle_id, data, organiser_id)

@obstacle_router.post("/unmap", status_code=status.HTTP_200_OK)
async def unmap_obstacle_from_track(track_id: int, obstacle_id: int, organiser_id: int, db: AsyncSession = Depends(get_db)):
    return await service.unmap_obstacle_from_track(db, track_id, obstacle_id, organiser_id)

registration_router = APIRouter(prefix="/api/registration", tags=["Registrations"])

@registration_router.get("/{registration_id}", response_model=RegistrationResponse, status_code=status.HTTP_200_OK)
async def get_registration(registration_id: int, db: AsyncSession = Depends(get_db)):
    return await service.get_registration_by_id(db, registration_id)  

@registration_router.get("/{participant_id}/participant", response_model=List[RegistrationResponse], status_code=status.HTTP_200_OK)
async def get_registrations_by_participant_id(participant_id: int, db: AsyncSession = Depends(get_db)):
    return await service.get_registrations_by_participant_id(db, participant_id)

@registration_router.post("/", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED)
async def create_registration(data: RegistrationCreate, db: AsyncSession = Depends(get_db)):
    return await service.create_registration(db, data)

@registration_router.delete("/{registration_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_registration(registration_id: int, participant_id: int, db: AsyncSession = Depends(get_db)):
    await service.delete_registration(db, registration_id, participant_id)