from pydantic import BaseModel, EmailStr, ConfigDict, Field, HttpUrl, field_validator
from app.enum import GenderEnum, TshirtSizeEnum
from datetime import UTC, date, datetime

class UserBase(BaseModel):
    email: EmailStr
    first_name: str 
    last_name: str

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, value):
        value = value.strip()
        if len(value) < 2 or len(value) > 50:
            raise ValueError("Name must be between 2 and 50 characters")
        return value
    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        value = value.strip()
        if len(value) > 50:
            raise ValueError("Email must be less than 50 characters")
        return value

class ParticipantCreate(UserBase):
    password: str
    date_of_birth: date
    gender: GenderEnum
    tshirt_size: TshirtSizeEnum | None = None
    emergency_contact: str
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, value):
        if len(value) < 8 or len(value) > 24:
            raise ValueError("Password must be between 8 and 24 characters")
        return value
    @field_validator('date_of_birth')
    @classmethod
    def validate_date_of_birth(cls, value):
        today = datetime.now(UTC).date()
        if value > today:
            raise ValueError("Date of birth cannot be in the future")
        if value < date(1900, 1, 1):
            raise ValueError("Date of birth cannot be before January 1, 1900")
        age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
        if age < 18:
            raise ValueError("User must be at least 18 years old")
        return value
    @field_validator('emergency_contact')
    @classmethod
    def validate_emergency_contact(cls, value):
        value = value.strip()
        if len(value) < 10 or len(value) > 20:
            raise ValueError("Emergency contact must be between 10 and 20 characters")
        return value

class OrganiserCreate(UserBase):
    password: str 
    organization_name: str 
    website: str | None 
    description: str 

    @field_validator('password')
    @classmethod
    def validate_password(cls, value):
        if len(value) < 8 or len(value) > 24:
            raise ValueError("Password must be between 8 and 24 characters")
        return value
    @field_validator('organization_name')
    @classmethod
    def validate_organization_name(cls, value):
        if len(value) < 2 or len(value) > 100:
            raise ValueError("Organization name must be between 2 and 100 characters")
        return value
    @field_validator('description')
    @classmethod
    def validate_description(cls, value):
        if len(value) < 10 or len(value) > 1000:
            raise ValueError("Description must be between 10 and 1000 characters")
        return value
    @field_validator('website')
    @classmethod
    def validate_website(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if value == "":
            return None
        if not value.startswith(("http://", "https://")):
            raise ValueError("Website URL must start with http:// or https://")
        if len(value) > 200:
            raise ValueError("Website URL must be less than 200 characters")
        return value

class AdminCreate(UserBase):
    password: str
    admin_level: int
    @field_validator('password')
    @classmethod
    def validate_password(cls, value):
        if len(value) < 8 or len(value) > 24:
            raise ValueError("Password must be between 8 and 24 characters")
        return value 
    @field_validator('admin_level')
    @classmethod
    def validate_admin_level(cls, value):
        if value < 1 or value > 5:
            raise ValueError("Admin level must be between 1 and 5")
        return value

class ParticipantDetails(BaseModel):
    date_of_birth: date
    gender: GenderEnum
    tshirt_size: TshirtSizeEnum | None
    emergency_contact: str

    model_config = ConfigDict(from_attributes=True)

class OrganiserDetails(BaseModel):
    organization_name: str
    website: str | None 
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

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

#Token response model

class TokenResponse(BaseModel):
    access_token: str
    token_type: str 
