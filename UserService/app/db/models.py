from datetime import datetime, date
from sqlalchemy import DateTime, Integer, String, Boolean, ForeignKey, Date, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Enum as SAEnum
from app.db.db import Base
from app.enum import GenderEnum, TshirtSizeEnum

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)    
    email: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(128))
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("NOW()"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    participant = relationship("Participant", back_populates="user", uselist=False)
    organiser = relationship("Organiser", back_populates="user", uselist=False)
    admin = relationship("Admin", back_populates="user", uselist=False)

class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), primary_key=True)
    admin_level: Mapped[int] = mapped_column(Integer, default=1)

    user = relationship("User", back_populates="admin")

class Participant(Base):
    __tablename__ = "participants"

    id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), primary_key=True)
    date_of_birth: Mapped[date] = mapped_column(Date)
    gender: Mapped[GenderEnum] = mapped_column(SAEnum(GenderEnum, name="gender_enum"))    
    tshirt_size: Mapped[TshirtSizeEnum | None] = mapped_column(SAEnum(TshirtSizeEnum, name="tshirt_size_enum"))
    emergency_contact: Mapped[str] = mapped_column(String(100))

    user = relationship("User", back_populates="participant")


class Organiser(Base):
    __tablename__ = "organisers"

    id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), primary_key=True)
    organization_name: Mapped[str] = mapped_column(String(100))
    website: Mapped[str | None] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(String(200))
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    
    user = relationship("User", back_populates="organiser")