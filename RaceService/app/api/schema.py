from typing import List
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from app.enum import RaceStatusEnum, TerrainTypeEnum, PaymentStatusEnum, DifficultyScoreEnum
from datetime import datetime, timezone


class TrackBase(BaseModel):
    length_km: float
    elevation_gain: int
    terrain_type: TerrainTypeEnum
    description: str | None = None

    @field_validator("length_km")
    @classmethod
    def length_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Length must be greater than 0")
        return v

    @field_validator("elevation_gain")
    @classmethod
    def elevation_must_be_positive(cls, v):
        if v < 0:
            raise ValueError("Elevation gain must be a positive number")
        return v


class RaceBase(BaseModel):
    name: str
    date_time: datetime
    deadline: datetime
    location: str
    max_participants: int
    status: RaceStatusEnum
    price: float

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()

    @field_validator("max_participants")
    @classmethod
    def participants_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Number of participants must be greater than 0")
        return v

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v):
        if v < 0:
            raise ValueError("Price must be a positive number")
        return v

    @model_validator(mode="after")
    def deadline_before_race(self):
        if self.deadline >= self.date_time:
            raise ValueError("Deadline must be before the race date")
        if self.date_time <= datetime.now(timezone.utc):
            raise ValueError("Race date must be in the future")
        return self


class RegistrationBase(BaseModel):
    payment_status: PaymentStatusEnum
    bib_number: str
    track_id: int
    @field_validator("bib_number")
    @classmethod
    def bib_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Bib number cannot be empty")
        return v.strip()


class ObstacleBase(BaseModel):
    name: str
    description: str | None = None
    difficulty_score: DifficultyScoreEnum

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Obstacle name cannot be empty")
        return v.strip()

## Response models

class TrackResponse(TrackBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class RaceResponse(RaceBase):
    id: int
    organiser_id: int
    created_at: datetime
    is_active: bool
    tracks: List[TrackResponse] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)

class RegistrationResponse(RegistrationBase):
    id: int
    race_id: int
    participant_id: int
    registration_date: datetime
    model_config = ConfigDict(from_attributes=True)

class ObstacleResponse(ObstacleBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

## Create/Update models

class TrackCreate(TrackBase):
    pass

class RaceCreate(RaceBase):
    tracks: List[TrackCreate]

    @field_validator("tracks")
    @classmethod
    def must_have_at_least_one_track(cls, v):
        if len(v) == 0:
            raise ValueError("Race must have at least one track")
        return v

class ObstacleCreate(ObstacleBase):
    pass

class RegistrationCreate(RegistrationBase):
    pass