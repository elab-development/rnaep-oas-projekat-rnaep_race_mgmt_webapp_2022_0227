from datetime import datetime, date
from sqlalchemy import DateTime, Integer, String, Boolean, ForeignKey, Date, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)    
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String)
    first_name: Mapped[str] = mapped_column(String)
    last_name: Mapped[str] = mapped_column(String)
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
    gender: Mapped[str] = mapped_column(String)    
    tshirt_size: Mapped[str | None] = mapped_column(String)
    emergency_contact: Mapped[str] = mapped_column(String)

    user = relationship("User", back_populates="participant")


class Organiser(Base):
    __tablename__ = "organisers"

    id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), primary_key=True)
    organization_name: Mapped[str] = mapped_column(String)
    website: Mapped[str | None] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    
    user = relationship("User", back_populates="organiser")