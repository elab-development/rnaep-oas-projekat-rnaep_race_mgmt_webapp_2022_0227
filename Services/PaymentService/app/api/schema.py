from datetime import datetime
from pydantic import BaseModel
from app.enum import PaymentStatusEnum as PaymentStatus

class PaymentCreate(BaseModel):
    registration_id: int
    amount: float


class PaymentResponse(BaseModel):
    id: int
    user_id: int
    registration_id: int
    stripe_session_id: str
    status: PaymentStatus
    amount: float
    checkout_url: str | None = None
    model_config = {"from_attributes": True}
    created_at: datetime


class CheckoutResponse(BaseModel):
    checkout_url: str