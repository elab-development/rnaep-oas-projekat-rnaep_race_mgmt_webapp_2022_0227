from sqlalchemy.orm import selectinload
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.enum import PaymentStatusEnum
from app.api.schema import RaceCreate, CreateObstacle, CreateRegistration
from app.db.models import Obstacle, Race, Registration, Track, TrackObstacle



# Repository functions for RaceService
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
            status=data.status,
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
        

async def patch_race(db: AsyncSession, race_id: int, data: dict) -> Race | None:
    try:
        race = await get_race_by_id(db, race_id)
        if not race:
            return None
        for key, val in data.items():
            if val is not None:
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
#Registration repository functions

async def get_registration_by_id(db: AsyncSession, registration_id: int) -> Registration | None:
    result = await db.execute(
        select(Registration).where(Registration.id == registration_id)
    )
    return result.scalar_one_or_none()

async def get_registrations_by_race_id(db: AsyncSession, race_id: int) -> list[Registration]:
    result = await db.execute(
        select(Registration).where(
            and_(
                Registration.race_id == race_id,
                Registration.payment_status == PaymentStatusEnum.COMPLETED
            )
        )
    )
    return result.scalars().all() 

async def get_registrations_by_participant_id(db: AsyncSession, participant_id: int) -> list[Registration]:
    result = await db.execute(
        select(Registration).where(Registration.participant_id == participant_id)    
    )
    return result.scalars().all()

async def create_registration(db: AsyncSession, participant_id: int, race_id: int, track_id: int, data: CreateRegistration) -> Registration | None:
    try:
        registration_model = Registration(
            participant_id=participant_id,
            race_id=race_id,
            track_id=track_id,
            payment_status=data.payment_status,
            bib_number=data.bib_number
        )
        db.add(registration_model)
        await db.commit()
        await db.refresh(registration_model)
        return registration_model
    except Exception as e:
        await db.rollback()
        raise e

async def delete_registration(db: AsyncSession, registration_id: int) -> bool:
    try:
        registration = await get_registration_by_id(db, registration_id)
        if not registration:
            return False
        await db.delete(registration)
        await db.commit()
        return True
    except Exception as e:
        await db.rollback()
        raise e