from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.api.schema import CreateObstacle, ObstacleResponse, ObstacleUpdate,TrackObstacleCreate
from app.db.repositories import obstacle_repository  
#Obstacle service functions 

async def get_obstacle_by_id(db: AsyncSession, obstacle_id: int):
    obstacle = await obstacle_repository.get_obstacle_by_id(db, obstacle_id)
    if not obstacle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Obstacle not found")
    return ObstacleResponse.model_validate(obstacle)

async def add_obstacle(db: AsyncSession, data: CreateObstacle, organiser_id: int):
    obstacle = await obstacle_repository.add_obstacle(db, data, organiser_id)
    return ObstacleResponse.model_validate(obstacle)

async def patch_obstacle(db: AsyncSession, obstacle_id: int, data: ObstacleUpdate, organiser_id: int):
    obstacle = await obstacle_repository.get_obstacle_by_id(db, obstacle_id)
    if not obstacle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Obstacle not found")
    if obstacle.organiser_id != organiser_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this obstacle")
    
    updated_obstacle = await obstacle_repository.patch_obstacle(db, obstacle_id, data.model_dump(exclude_unset=True))
    return ObstacleResponse.model_validate(updated_obstacle)

async def delete_obstacle(db: AsyncSession, obstacle_id: int, organiser_id: int):
    obstacle = await obstacle_repository.get_obstacle_by_id(db, obstacle_id)
    if not obstacle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Obstacle not found")
    if obstacle.organiser_id != organiser_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this obstacle")
    
    return await obstacle_repository.delete_obstacle(db, obstacle_id)

async def map_obstacle_to_track(db: AsyncSession, track_id: int, obstacle_id: int, data: TrackObstacleCreate, organiser_id: int):
    track = await obstacle_repository.get_track_by_id(db, track_id)
    if not track:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Track not found")
    race = await obstacle_repository.get_race_by_id(db, track.race_id)
    if race.organiser_id != organiser_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to modify this track")
    obstacle = await obstacle_repository.get_obstacle_by_id(db, obstacle_id)
    if not obstacle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Obstacle not found")
    if obstacle.organiser_id != organiser_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to modify this obstacle")
    track_obstacle = await obstacle_repository.map_obstacle_to_track(db, track_id, obstacle_id, data.order, data.distance_from_start_km)
    return track_obstacle

async def unmap_obstacle_from_track(db: AsyncSession, track_id: int, obstacle_id: int, organiser_id: int):
    track = await obstacle_repository.get_track_by_id(db, track_id)
    if not track:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Track not found")
    race = await obstacle_repository.get_race_by_id(db, track.race_id)
    if race.organiser_id != organiser_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to modify this track")
    obstacle = await obstacle_repository.get_obstacle_by_id(db, obstacle_id)
    if not obstacle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Obstacle not found")
    if obstacle.organiser_id != organiser_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to modify this obstacle")
    return await obstacle_repository.unmap_obstacle_from_track(db, track_id, obstacle_id)
