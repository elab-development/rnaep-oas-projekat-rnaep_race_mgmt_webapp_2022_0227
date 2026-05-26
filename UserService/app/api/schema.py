from pydantic import BaseModel, EmailStr, ConfigDict, Field, HttpUrl
from app.enum import GenderEnum, TshirtSizeEnum
from datetime import date, datetime

class UserBase(BaseModel):
    email: EmailStr = Field(min_length=5, max_length=50)
    first_name: str = Field(min_length=2, max_length=50)
    last_name: str = Field(min_length=2, max_length=50)

class ParticipantCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)
    date_of_birth: date
    gender: GenderEnum
    tshirt_size: TshirtSizeEnum | None = None
    emergency_contact: str = Field(min_length=5, max_length=100)

class OrganiserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)
    organization_name: str = Field(min_length=2, max_length=100)
    website: str | None = Field(default=None, pattern=r"^(https?://.*)?$")
    description: str = Field(min_length=10, max_length=200)

class AdminCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)
    admin_level: int = Field(default=1, ge=1, le=5)


class ParticipantDetails(BaseModel):
    date_of_birth: date
    gender: GenderEnum
    tshirt_size: TshirtSizeEnum | None
    emergency_contact: str

    model_config = ConfigDict(from_attributes=True)

class OrganiserDetails(BaseModel):
    organization_name: str
    website: str | None = Field(default=None, pattern=r"^(https?://.*)?$")
    description: str
    is_verified: bool

    model_config = ConfigDict(from_attributes=True)

class AdminDetails(BaseModel):
    admin_level: int

    model_config = ConfigDict(from_attributes=True)

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    participant: ParticipantDetails | None = Field(default=None)
    organiser: OrganiserDetails | None = Field(default=None)
    admin: AdminDetails | None = Field(default=None)

    model_config = ConfigDict(from_attributes=True)


#Token response model

class TokenResponse(BaseModel):
    access_token: str
    token_type: str 