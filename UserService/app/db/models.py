from sqlalchemy import Column, DateTime, Integer, String, Boolean, ForeignKey, Date, text
from sqlalchemy.orm import relationship
from db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=text("NOW()"))
    is_active = Column(Boolean, default=True)

    participant = relationship("Participant", back_populates="user", uselist=False)
    organiser = relationship("Organiser", back_populates="user", uselist=False)
    admin = relationship("Admin", back_populates="user", uselist=False)

class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    admin_level = Column(Integer, default=1)

    user = relationship("User", back_populates="admin")

class Participant(Base):
    __tablename__ = "participants"

    id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    date_of_birth = Column(Date)
    gender = Column(String)
    tshirt_size = Column(String)
    emergency_contact = Column(String)

    user = relationship("User", back_populates="participant")

class Organiser(Base):
    __tablename__ = "organisers"

    id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    organization_name = Column(String)
    website = Column(String)
    description = Column(String)
    is_verified = Column(Boolean, default=False)

    user = relationship("User", back_populates="organiser")

