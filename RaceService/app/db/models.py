from datetime import datetime
from decimal import Decimal
from sqlalchemy import DateTime, Integer, String, Boolean, ForeignKey, UniqueConstraint, text, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Enum as SAEnum
from app.db.db import Base
from app.enum import RaceStatusEnum, TerrainTypeEnum, PaymentStatusEnum, DifficultyScoreEnum

class Race(Base):
    __tablename__ = "races"
    id: Mapped[int] = mapped_column(primary_key=True)
    organiser_id: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(100))
    date_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    location: Mapped[str] = mapped_column(String(200))
    max_participants: Mapped[int] = mapped_column(Integer)
    status: Mapped[RaceStatusEnum] = mapped_column(SAEnum(RaceStatusEnum, name="race_status_enum"))
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("NOW()"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    #relationships
    tracks: Mapped[list["Track"]] = relationship("Track", back_populates="race", cascade="all, delete-orphan")
    registrations: Mapped[list["Registration"]] = relationship("Registration", back_populates="race", cascade="all, delete-orphan")

class Track(Base):
    __tablename__ = "tracks"

    id: Mapped[int] = mapped_column(primary_key=True)
    race_id: Mapped[int] = mapped_column(Integer, ForeignKey("races.id", ondelete="CASCADE"))
    length_km: Mapped[Decimal] = mapped_column(Numeric(6, 2))
    elevation_gain: Mapped[int] = mapped_column(Integer)
    terrain_type: Mapped[TerrainTypeEnum] = mapped_column(SAEnum(TerrainTypeEnum, name="terrain_type_enum"))
    description: Mapped[str | None] = mapped_column(String(500))

    #relationships
    trackobstacles: Mapped[list["TrackObstacle"]] = relationship("TrackObstacle", back_populates="track")
    race: Mapped["Race"] = relationship("Race", back_populates="tracks")
    registrations: Mapped[list["Registration"]] = relationship("Registration", back_populates="track")

class Registration(Base):
    __tablename__ = "registrations"

    __table_args__ = (
    UniqueConstraint("race_id", "participant_id", "track_id", name="uq_race_participant_track"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    race_id: Mapped[int] = mapped_column(Integer, ForeignKey("races.id", ondelete="CASCADE"))
    track_id: Mapped[int] = mapped_column(Integer, ForeignKey("tracks.id", ondelete="CASCADE"))
    participant_id: Mapped[int] = mapped_column(Integer) 
    registration_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("NOW()"))
    payment_status: Mapped[PaymentStatusEnum] = mapped_column(SAEnum(PaymentStatusEnum, name="payment_status_enum"))
    bib_number: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("NOW()"))

    #relationships
    race: Mapped["Race"] = relationship("Race", back_populates="registrations")
    track: Mapped["Track"] = relationship("Track", back_populates="registrations")

class Obstacle(Base):
    __tablename__ = "obstacles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(String(500))
    difficulty_score: Mapped[DifficultyScoreEnum] = mapped_column(SAEnum(DifficultyScoreEnum, name="difficulty_score_enum"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("NOW()"))

    trackobstacles: Mapped[list["TrackObstacle"]] = relationship("TrackObstacle", back_populates="obstacle")

class TrackObstacle(Base):
    __tablename__ = "track_obstacles"

    track_id: Mapped[int] = mapped_column(Integer, ForeignKey("tracks.id", ondelete="CASCADE"), primary_key=True)
    obstacle_id: Mapped[int] = mapped_column(Integer, ForeignKey("obstacles.id", ondelete="RESTRICT"), primary_key=True)
    order: Mapped[int] = mapped_column(Integer)
    distance_from_start_km: Mapped[Decimal] = mapped_column(Numeric(6, 2))

    #relationships

    track: Mapped["Track"] = relationship("Track", back_populates="trackobstacles")
    obstacle: Mapped["Obstacle"] = relationship("Obstacle", back_populates="trackobstacles")