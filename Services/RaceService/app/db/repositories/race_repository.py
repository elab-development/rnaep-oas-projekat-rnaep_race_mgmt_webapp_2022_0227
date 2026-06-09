from sqlalchemy.orm import selectinload
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.schema import RaceCreate
from app.db.models import Race



# Repository functions for RaceService
async def get_race_by_id(db: AsyncSession, race_id: int) -> Race | None:
    result = await db.execute(
        select(Race).where(Race.id == race_id)
    )
    return result.scalar_one_or_none()

async def create_race(db: AsyncSession, data: RaceCreate, organiser_id: int) -> Race:
    try:
        race_model = Race(
            organiser_id=organiser_id,
            name= data.name,
            date_time=data.date_time,
            deadline=data.deadline,
            location=data.location,
            max_participants=data.max_participants,
            status=data.status,
            price=data.price,
        )
        db.add(race_model)
        await db.commit()
        result = await db.execute(
            select(Race).where(Race.id == race_model.id)
        )
        return result.scalar_one()
    except Exception as e:
        await db.rollback()
        raise e
        

async def patch_race(db: AsyncSession, race_id: int, data: dict) -> Race | None:
    try:
        race = await get_race_by_id(db, race_id)
        if not race:
            return None
        for key, val in data.items():
                setattr(race, key, val)
        await db.commit()
        await db.refresh(race)
        return race
    except Exception as e:
        await db.rollback()
        raise e
    
async def delete_race(db: AsyncSession, race_id: int) -> bool:
    try:
        race = await get_race_by_id(db, race_id)
        if not race:
            return False
        await db.delete(race)
        await db.commit()
        return True
    except Exception as e:
        await db.rollback()
        raise e