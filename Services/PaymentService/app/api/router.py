from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.db import get_db
from app import service
from app.api.schema import PaymentCreate, PaymentResponse, CheckoutResponse

router = APIRouter(prefix="/payments", tags=["payments"])

@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout(
    body: PaymentCreate,
    db: AsyncSession = Depends(get_db),
):
    return await service.create_checkout_session(
        db, body.user_id, body.registration_id, body.amount
    )

@router.get("/me/{user_id}", response_model=list[PaymentResponse])
async def get_my_payments(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    payments = await service.get_payments_by_user_id(db, user_id)
    return [PaymentResponse.model_validate(p) for p in payments]

@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await service.get_payment_by_id(db, payment_id)

@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(alias="stripe-signature"),
    db: AsyncSession = Depends(get_db)
):
    payload = await request.body()
    return await service.handle_webhook(db, payload, stripe_signature)