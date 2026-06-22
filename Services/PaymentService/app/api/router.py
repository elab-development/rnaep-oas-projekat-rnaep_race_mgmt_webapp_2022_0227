from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_current_user, require_participant
from app.db.db import get_db
from app import service
from app.api.schema import PaymentCreate, PaymentResponse, CheckoutResponse

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout(
    body: PaymentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_participant)
):
    user_id = int(current_user["sub"])
    participant_email = current_user.get("email", "")
    participant_name = current_user.get("username", "")
    return await service.create_checkout_session(
        db, user_id, body.registration_id, body.amount, participant_email, participant_name
    )


@router.get("/me", response_model=list[PaymentResponse])
async def get_my_payments(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    user_id = int(current_user["sub"])
    payments = await service.get_payments_by_user_id(db, user_id)
    return [PaymentResponse.model_validate(p) for p in payments]


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user), 
):
    user_id = int(current_user["sub"])
    return await service.get_payment_by_id(db, payment_id, user_id)


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(alias="stripe-signature"),
    db: AsyncSession = Depends(get_db)
):
    payload = await request.body()
    return await service.handle_webhook(db, payload, stripe_signature)