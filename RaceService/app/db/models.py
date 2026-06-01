from datetime import datetime
from decimal import Decimal
from sqlalchemy import DateTime, Integer, String, Boolean, ForeignKey, UniqueConstraint, text, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Enum as SAEnum
from app.db.db import Base
from app.enum import RaceStatusEnum, PaymentStatusEnum

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
    registrations: Mapped[list["Registration"]] = relationship("Registration", back_populates="race", cascade="all, delete-orphan")

class Registration(Base):
    __tablename__ = "registrations"

    id: Mapped[int] = mapped_column(primary_key=True)
    race_id: Mapped[int] = mapped_column(Integer, ForeignKey("races.id", ondelete="CASCADE"))
    participant_id: Mapped[int] = mapped_column(Integer) 
    registration_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("NOW()"))
    payment_status: Mapped[PaymentStatusEnum] = mapped_column(SAEnum(PaymentStatusEnum, name="payment_status_enum"))
    bib_number: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("NOW()"))

    #relationships
    race: Mapped["Race"] = relationship("Race", back_populates="registrations")