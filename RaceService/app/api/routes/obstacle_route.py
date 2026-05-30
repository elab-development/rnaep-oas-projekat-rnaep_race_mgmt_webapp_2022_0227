from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, status
from app.db.db import get_db
from app.api.schema import CreateObstacle, ObstacleResponse, ObstacleUpdate, TrackObstacleCreate
from app.services import obstacle_service


obstacle_router = APIRouter(prefix="/api/obstacle", tags=["Obstacles"])

@obstacle_router.get("/{obstacle_id}", response_model=ObstacleResponse, status_code=status.HTTP_200_OK)
async def get_obstacle(obstacle_id: int, db: AsyncSession = Depends(get_db)):
    return await obstacle_service.get_obstacle_by_id(db, obstacle_id)

@obstacle_router.post("/", response_model=ObstacleResponse, status_code=status.HTTP_201_CREATED)
async def create_obstacle(data: CreateObstacle, organiser_id: int, db: AsyncSession = Depends(get_db)):
    return await obstacle_service.add_obstacle(db, data, organiser_id)   

@obstacle_router.patch("/{obstacle_id}", response_model=ObstacleResponse, status_code=status.HTTP_200_OK)
async def update_obstacle(obstacle_id: int, data: ObstacleUpdate, organiser_id: int, db: AsyncSession = Depends(get_db)):
    return await obstacle_service.patch_obstacle(db, obstacle_id, data, organiser_id)

@obstacle_router.post("/{obstacle_id}/tracks/{track_id}", response_model=TrackObstacleCreate, status_code=status.HTTP_201_CREATED)
async def map_obstacle_to_track(obstacle_id: int, track_id: int, data: TrackObstacleCreate, organiser_id: int, db: AsyncSession = Depends(get_db)):
    return await obstacle_service.map_obstacle_to_track(db, track_id, obstacle_id, data, organiser_id)

@obstacle_router.delete("/{obstacle_id}/tracks/{track_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unmap_obstacle_from_track(obstacle_id: int, track_id: int, organiser_id: int, db: AsyncSession = Depends(get_db)):
    await obstacle_service.unmap_obstacle_from_track(db, track_id, obstacle_id, organiser_id)