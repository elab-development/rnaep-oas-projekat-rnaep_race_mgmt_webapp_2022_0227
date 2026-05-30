from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.api.schema import CreateObstacle, ObstacleResponse, ObstacleUpdate, RaceCreate, RaceResponse, RegistrationCreate, RegistrationResponse, RegistrationResponse, TrackCreate, TrackObstacleCreate, TrackResponse, TrackUpdate, UpdateRace
from app.db import repository


# Service functions for Race
async def get_race_by_id(db: AsyncSession, race_id: int):
    race = await repository.get_race_by_id(db, race_id)
    if not race:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Race not found")
    return RaceResponse.model_validate(race)

async def create_race(db: AsyncSession, data: RaceCreate, organiser_id: int):
    race = await repository.create_race(db, data, organiser_id)
    return RaceResponse.model_validate(race)

async def patch_race(db: AsyncSession, race_id: int, organiser_id: int, data: UpdateRace):
    race = await repository.get_race_by_id(db, race_id)
    if not race:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Race not found")
    if race.organiser_id != organiser_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this race")
    updated_race = await repository.patch_race(db, race_id, data.model_dump(exclude_unset=True))
    return RaceResponse.model_validate(updated_race)

async def delete_race(db: AsyncSession, race_id: int, organiser_id: int):
    race = await repository.get_race_by_id(db, race_id)
    if not race:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Race not found")
    if race.organiser_id != organiser_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this race")
    return await repository.delete_race(db, race_id)   

#Service function for Track

async def get_track_by_id(db: AsyncSession, track_id: int):
    track = await repository.get_track_by_id(db, track_id)
    if not track:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Track not found")
    return TrackResponse.model_validate(track)

async def patch_track(db: AsyncSession, track_id: int, organiser_id: int, data: TrackUpdate):
    track = await repository.get_track_by_id(db, track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    
    race = await repository.get_race_by_id(db, track.race_id)
    if race.organiser_id != organiser_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this track")
    
    updated_track = await repository.patch_track(db, track_id, data.model_dump(exclude_unset=True))
    return TrackResponse.model_validate(updated_track)

async def delete_track(db: AsyncSession, track_id: int, organiser_id: int):
    track = await repository.get_track_by_id(db, track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    
    race = await repository.get_race_by_id(db, track.race_id)
    if race.organiser_id != organiser_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this track")
    
    return await repository.delete_track(db, track_id)

async def add_track_to_race(db: AsyncSession, race_id: int, organiser_id: int, data: TrackCreate):
    race = await repository.get_race_by_id(db, race_id)
    if not race:
        raise HTTPException(status_code=404, detail="Race not found")
    if race.organiser_id != organiser_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    track = await repository.add_track_to_race(db, race_id, data.model_dump(exclude_unset=True))
    return TrackResponse.model_validate(track)

#Obstacle service functions 

async def get_obstacle_by_id(db: AsyncSession, obstacle_id: int):
    obstacle = await repository.get_obstacle_by_id(db, obstacle_id)
    if not obstacle:
        raise HTTPException(status_code=404, detail="Obstacle not found")
    return ObstacleResponse.model_validate(obstacle)

async def add_obstacle(db: AsyncSession, data: CreateObstacle, organiser_id: int):
    obstacle = await repository.add_obstacle(db, data, organiser_id)
    return ObstacleResponse.model_validate(obstacle)

async def patch_obstacle(db: AsyncSession, obstacle_id: int, data: ObstacleUpdate, organiser_id: int):
    obstacle = await repository.get_obstacle_by_id(db, obstacle_id)
    if not obstacle:
        raise HTTPException(status_code=404, detail="Obstacle not found")
    if obstacle.organiser_id != organiser_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this obstacle")
    
    updated_obstacle = await repository.patch_obstacle(db, obstacle_id, data.model_dump(exclude_unset=True))
    return ObstacleResponse.model_validate(updated_obstacle)

async def delete_obstacle(db: AsyncSession, obstacle_id: int, organiser_id: int):
    obstacle = await repository.get_obstacle_by_id(db, obstacle_id)
    if not obstacle:
        raise HTTPException(status_code=404, detail="Obstacle not found")
    if obstacle.organiser_id != organiser_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this obstacle")
    
    return await repository.delete_obstacle(db, obstacle_id)

async def map_obstacle_to_track(db: AsyncSession, track_id: int, obstacle_id: int, data: TrackObstacleCreate, organiser_id: int):
    track = await repository.get_track_by_id(db, track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    race = await repository.get_race_by_id(db, track.race_id)
    if race.organiser_id != organiser_id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this track")
    obstacle = await repository.get_obstacle_by_id(db, obstacle_id)
    if not obstacle:
        raise HTTPException(status_code=404, detail="Obstacle not found")
    if obstacle.organiser_id != organiser_id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this obstacle")
    track_obstacle = await repository.map_obstacle_to_track(db, track_id, obstacle_id, data.order, data.distance_from_start_km)
    return track_obstacle

async def unmap_obstacle_from_track(db: AsyncSession, track_id: int, obstacle_id: int, organiser_id: int):
    track = await repository.get_track_by_id(db, track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")
    race = await repository.get_race_by_id(db, track.race_id)
    if race.organiser_id != organiser_id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this track")
    obstacle = await repository.get_obstacle_by_id(db, obstacle_id)
    if not obstacle:
        raise HTTPException(status_code=404, detail="Obstacle not found")
    if obstacle.organiser_id != organiser_id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this obstacle")
    return await repository.unmap_obstacle_from_track(db, track_id, obstacle_id)

#Registration service

async def get_registration_by_id(db: AsyncSession, registration_id: int):
    registration = await repository.get_registration_by_id(db, registration_id)
    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")
    return RegistrationResponse.model_validate(registration)

async def get_registrations_by_participant_id(db: AsyncSession, participant_id: int):
    registrations = await repository.get_registrations_by_participant_id(db, participant_id)
    return [RegistrationResponse.model_validate(reg) for reg in registrations]

async def create_registration(db: AsyncSession, participant_id: int, race_id: int, track_id: int, data: RegistrationCreate):
    registration = await repository.create_registration(db, participant_id, race_id, track_id, data)
    if not registration:    
        raise HTTPException(status_code=400, detail="Registration failed. Possible reasons: invalid race or track ID, registration already exists for this participant on the same track, or race registration deadline has passed.")
    return RegistrationResponse.model_validate(registration)

async def delete_registration(db: AsyncSession, registration_id: int, participant_id: int):
    registration = await repository.get_registration_by_id(db, registration_id)
    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")
    if registration.participant_id != participant_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this registration")
    return await repository.delete_registration(db, registration_id)
