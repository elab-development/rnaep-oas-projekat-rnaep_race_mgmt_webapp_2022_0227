from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.repositories.track_repository import get_track_by_id
from app.api.schema import CreateObstacle
from app.db.models import Obstacle, TrackObstacle

#Obstacle repository functions

async def get_obstacle_by_id(db: AsyncSession, obstacle_id: int) -> Obstacle | None:
    result = await db.execute(
        select(Obstacle).where(Obstacle.id == obstacle_id)
    )
    return result.scalar_one_or_none()

async def add_obstacle(db: AsyncSession, obstacle_data: CreateObstacle, organiser_id: int) -> Obstacle | None:
    try:
        obstacle_model = Obstacle(
            name=obstacle_data.name,
            description=obstacle_data.description,
            difficulty_score=obstacle_data.difficulty_score,
            organiser_id=organiser_id
        )
        db.add(obstacle_model)
        await db.commit()
        await db.refresh(obstacle_model)
        return obstacle_model
    except Exception as e:
        await db.rollback()
        raise e

async def patch_obstacle(db: AsyncSession, obstacle_id: int, data: dict) -> Obstacle | None:
    try:
        obstacle = await get_obstacle_by_id(db, obstacle_id)
        if not obstacle:
            return None
        for key, val in data.items():
            if val is not None:
                setattr(obstacle, key, val)
        await db.commit()
        await db.refresh(obstacle)
        return obstacle
    except Exception as e:
        await db.rollback()
        raise e

async def delete_obstacle(db: AsyncSession, obstacle_id: int) -> bool:
    try:
        obstacle = await get_obstacle_by_id(db, obstacle_id)
        if not obstacle:
            return False
        await db.delete(obstacle)
        await db.commit()
        return True
    except Exception as e:
        await db.rollback()
        raise e

async def map_obstacle_to_track(db: AsyncSession, track_id: int, obstacle_id: int, order: int, distance_from_start_km: float) -> TrackObstacle | None:
    try:
        track = await get_track_by_id(db, track_id)
        if not track:
            return None
        obstacle = await get_obstacle_by_id(db, obstacle_id)
        if not obstacle:
            return None
        track_obstacle = TrackObstacle(
            track_id=track_id,
            obstacle_id=obstacle_id,
            order=order,
            distance_from_start_km=distance_from_start_km
        )
        db.add(track_obstacle)
        await db.commit()
        await db.refresh(track_obstacle)
        return track_obstacle
    except Exception as e:
        await db.rollback()
        raise e

async def unmap_obstacle_from_track(db: AsyncSession, track_id: int, obstacle_id: int) -> bool:
    try:
        track_obstacle = await db.execute(
            select(TrackObstacle).where(
                TrackObstacle.track_id == track_id,
                TrackObstacle.obstacle_id == obstacle_id
            )
        )
        track_obstacle = track_obstacle.scalar_one_or_none()
        if not track_obstacle:
            return False
        await db.delete(track_obstacle)
        await db.commit()
        return True
    except Exception as e:
        await db.rollback()
        raise e