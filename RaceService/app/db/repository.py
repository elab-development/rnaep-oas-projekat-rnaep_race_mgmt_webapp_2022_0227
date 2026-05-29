from sqlalchemy.orm import selectinload
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.schema import RaceCreate
from app.db.models import Race, Track

async def get_race_by_id(db: AsyncSession, race_id: int) -> Race | None:
    result = await db.execute(
        select(Race)
        .options(
            selectinload(Race.tracks)
        ).where(Race.id == race_id)
    )
    return result.scalar_one_or_none()

async def create_race(db: AsyncSession, data: RaceCreate, organiser_id: int) -> Race:
    try:
        track_models = []
        for track in data.tracks:
            track_model = Track(
                length_km=track.length_km,
                elevation_gain=track.elevation_gain,
                terrain_type=track.terrain_type,
                description=track.description
            )
            track_models.append(track_model)
        
        race_model = Race(
            organiser_id=organiser_id,
            name= data.name,
            date_time=data.date_time,
            deadline=data.deadline,
            location=data.location,
            max_participants=data.max_participants,
            price=data.price,
            tracks=track_models
        )
        db.add(race_model)
        await db.commit()
        result = await db.execute(
            select(Race)
            .options(
                selectinload(Race.tracks)
            ).where(Race.id == race_model.id)
        )
        return result.scalar_one()
    except Exception as e:
        await db.rollback()
        raise e
        