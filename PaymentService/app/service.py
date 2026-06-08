import stripe
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.db import repository
from app.api.schema import CheckoutResponse, PaymentResponse
from app.config import settings
from app.enum import PaymentStatus


async def get_payment_by_id(db: AsyncSession, payment_id: int):
    payment = await repository.get_payment_by_id(db, payment_id)
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    return PaymentResponse.model_validate(payment)

async def create_checkout_session(
    db: AsyncSession,
    user_id: int,
    registration_id: int,
    amount: float
):
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "unit_amount": int(amount * 100),
                    "product_data": {
                        "name": f"ObstaRace - Registration {registration_id}" 
                    },
                },
                "quantity": 1  
            }],
            mode="payment",
            success_url = settings.STRIPE_SUCCESS_URL,
            cancel_url = settings.STRIPE_CANCEL_URL
        )
    except stripe.StripeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    payment = await repository.create_payment(
        db=db,
        user_id=user_id,
        registration_id=registration_id,
        stripe_session_id=session.id,
        amount=amount
    )
    return CheckoutResponse(checkout_url=session.url)

async def handle_webhook(db: AsyncSession, payload: bytes, sig_header: str):
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except (ValueError, stripe.SignatureVerificationError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    session = event["data"]["object"]

    if event["type"] == "checkout.session.completed":
        await repository.update_payment_status(db, session["id"], PaymentStatus.SUCCEEDED)
    elif event["type"] == "checkout.session.expired":
        await repository.update_payment_status(db, session["id"], PaymentStatus.FAILED)

    return {"status": "ok"}