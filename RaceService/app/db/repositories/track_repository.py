from sqlalchemy import  select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.repositories.race_repository import get_race_by_id
from app.db.models import Track

#Track repository functions
async def get_track_by_id(db: AsyncSession, track_id: int) -> Track | None:
    result = await db.execute(
        select(Track).where(Track.id == track_id)
    )
    return result.scalar_one_or_none()    

async def patch_track(db: AsyncSession, track_id: int, data: dict) -> Track | None:
    try:
        track = await get_track_by_id(db, track_id)
        if not track:
            return None
        for key, val in data.items():
            if val is not None:
                setattr(track, key, val)
        await db.commit()
        await db.refresh(track)
        return track
    except Exception as e:
        await db.rollback()
        raise e

async def delete_track(db: AsyncSession, track_id: int) -> bool:
    try:
        track = await get_track_by_id(db, track_id)
        if not track:
            return False
        await db.delete(track)
        await db.commit()
        return True
    except Exception as e:
        await db.rollback()
        raise e
    
async def add_track_to_race(db: AsyncSession, race_id: int, track_data: dict) -> Track | None:
    try:
        race = await get_race_by_id(db, race_id)
        if not race:
            return None
        track_model = Track(
            length_km=track_data["length_km"],
            elevation_gain=track_data["elevation_gain"],
            terrain_type=track_data["terrain_type"],
            description=track_data.get("description")
        )
        race.tracks.append(track_model)
        await db.commit()
        await db.refresh(track_model)
        return track_model
    except Exception as e:
        await db.rollback()
        raise e
