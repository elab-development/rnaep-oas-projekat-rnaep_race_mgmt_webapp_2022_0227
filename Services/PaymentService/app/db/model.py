from datetime import datetime, timezone
from sqlalchemy import Integer, String, DateTime, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Enum as SAEnum
from app.db.db import Base
from app.enum import PaymentStatus


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    registration_id: Mapped[int] = mapped_column(Integer, nullable=False)
    stripe_session_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    status: Mapped[PaymentStatus] = mapped_column(
        SAEnum(PaymentStatus),
        default=PaymentStatus.PENDING,
        nullable=False
    )
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    checkout_url: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    participant_email: Mapped[str] = mapped_column(String(100), nullable=False)
    participant_name: Mapped[str] = mapped_column(String(100), nullable=False)