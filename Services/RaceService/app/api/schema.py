from typing import List
from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator, model_validator
from app.enum import RaceStatusEnum, PaymentStatusEnum
from datetime import datetime, timezone


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
    
    @field_serializer("date_time", "deadline")
    def format_datetime(self, v: datetime) -> str:
        return v.strftime("%Y/%d/%m %H:%M")

class RegistrationBase(BaseModel):
    race_id: int
## Response models
class RaceResponse(RaceBase):
    id: int
    organiser_id: int
    created_at: datetime
    is_active: bool
    model_config = ConfigDict(from_attributes=True)

    @field_serializer("created_at")
    def format_created_at(self, v: datetime) -> str:
        return v.strftime("%Y/%d/%m %H:%M")

class RegistrationResponse(RegistrationBase):
    id: int
    race_id: int
    participant_id: int
    bib_number: str
    payment_status: PaymentStatusEnum
    registration_date: datetime
    model_config = ConfigDict(from_attributes=True)

## Create/Update models

class RaceCreate(RaceBase):
    @model_validator(mode="after")
    def deadline_before_race(self):
        if self.deadline >= self.date_time:
            raise ValueError("Deadline must be before the race date")
        if self.date_time <= datetime.now(timezone.utc):
            raise ValueError("Race date must be in the future")
        return self

class RegistrationCreate(RegistrationBase):
    pass

class RaceUpdate(BaseModel):
    name: str | None = None
    date_time: datetime | None = None
    deadline: datetime | None = None
    location: str | None = None
    max_participants: int | None = None
    status: RaceStatusEnum | None = None
    price: float | None = None