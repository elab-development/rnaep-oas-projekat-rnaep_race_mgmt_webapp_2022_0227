from pydantic import BaseModel
from app.enum import PaymentStatus

class PaymentCreate(BaseModel):
    user_id: int
    registration_id: int
    amount: float


class PaymentResponse(BaseModel):
    id: int
    user_id: int
    registration_id: int
    stripe_session_id: str
    status: PaymentStatus
    amount: float

    model_config = {"from_attributes": True}


class CheckoutResponse(BaseModel):
    checkout_url: str