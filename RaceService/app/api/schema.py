from typing import List
from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator, model_validator
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
    status: RaceStatusEnum = RaceStatusEnum.UPCOMING
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

    @field_serializer("date_time", "deadline")
    def format_datetime(self, v: datetime) -> str:
        return v.strftime("%Y/%d/%m %H:%M")

class RegistrationBase(BaseModel):
    payment_status: PaymentStatusEnum = PaymentStatusEnum.PENDING
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

    @field_serializer("created_at")
    def format_created_at(self, v: datetime) -> str:
        return v.strftime("%Y/%d/%m %H:%M")

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

class CreateObstacle(ObstacleBase):
    order: int
    distance_from_start_km: float
    
    @field_validator("distance_from_start_km")
    @classmethod
    def distance_must_be_positive(cls, v):
        if v < 0:
            raise ValueError("Distance from start must be a positive number")
        return v
    
    @field_validator("order")
    @classmethod
    def order_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Order must be greater than 0")
        return v

class RegistrationCreate(RegistrationBase):
    pass

class CreateTrack(TrackBase):
    pass

class TrackObstacleCreate(BaseModel):
    order: int
    distance_from_start_km: float
    
    @field_validator("distance_from_start_km")
    @classmethod
    def distance_must_be_positive(cls, v):
        if v < 0:
            raise ValueError("Distance from start must be a positive number")
        return v
    
    @field_validator("order")
    @classmethod
    def order_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Order must be greater than 0")
        return v

class RaceUpdate(BaseModel):
    name: str | None = None
    date_time: datetime | None = None
    deadline: datetime | None = None
    location: str | None = None
    max_participants: int | None = None
    status: RaceStatusEnum | None = None
    price: float | None = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip() if v else v

    @field_validator("price")
    @classmethod
    def price_positive(cls, v):
        if v is not None and v < 0:
            raise ValueError("Price must be a positive number")
        return v

class TrackUpdate(BaseModel):
    length_km: float | None = None
    elevation_gain: int | None = None
    terrain_type: TerrainTypeEnum | None = None
    description: str | None = None

    @field_validator("length_km")
    @classmethod
    def length_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Length must be greater than 0")
        return v

    @field_validator("elevation_gain")
    @classmethod
    def elevation_positive(cls, v):
        if v is not None and v < 0:
            raise ValueError("Elevation gain must be a positive number")
        return v
    
    @field_validator("terrain_type")
    @classmethod
    def terrain_type_valid(cls, v):
        if v is not None and v not in TerrainTypeEnum.__members__.values():
            raise ValueError("Invalid terrain type")
        return v

class ObstacleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    difficulty_score: DifficultyScoreEnum | None = None

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Obstacle name cannot be empty")
        return v.strip() if v else v
    @field_validator("difficulty_score")
    @classmethod
    def difficulty_score_valid(cls, v):
        if v is not None and v not in DifficultyScoreEnum.__members__.values():
            raise ValueError("Invalid difficulty score")
        return v