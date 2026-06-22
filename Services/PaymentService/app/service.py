import stripe
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.api.schema import PaymentResponse, CheckoutResponse
from app.db import repository
from app.config import settings
from app.kafka.producer import send_payment_completed, send_payment_failed
from app.enum import PaymentStatusEnum

stripe.api_key = settings.payment_secret_key.get_secret_value()


async def create_checkout_session(
    db: AsyncSession,
    user_id: int,
    registration_id: int,
    amount: float,
    participant_email: str,
    participant_name: str,
) -> CheckoutResponse:
    existing = await repository.get_payment_by_registration_id(db, registration_id)
    if existing:
        return CheckoutResponse(checkout_url=existing.checkout_url)

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "eur",
                    "product_data": {"name": f"Registracija #{registration_id}"},
                    "unit_amount": int(amount * 100),
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=settings.stripe_success_url,
            cancel_url=settings.stripe_cancel_url,
            metadata={
                "registration_id": str(registration_id),
                "user_id": str(user_id),
            },
        )
    except stripe.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e)
        )

    payment = await repository.create_payment(
        db=db,
        user_id=user_id,
        registration_id=registration_id,
        stripe_session_id=session.id,
        amount=amount,
        checkout_url=session.url,
        participant_email=participant_email,
        participant_name=participant_name,
    )
    return CheckoutResponse(checkout_url=payment.checkout_url)


async def get_payment_by_id(db: AsyncSession, payment_id: int, user_id: int) -> PaymentResponse:
    payment = await repository.get_payment_by_id(db, payment_id)
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    if payment.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return PaymentResponse.model_validate(payment)


async def get_payments_by_user_id(db: AsyncSession, user_id: int) -> list[PaymentResponse]:
    payments = await repository.get_payments_by_user_id(db, user_id)
    return [PaymentResponse.model_validate(p) for p in payments]


async def delete_payment_by_registration_id(db: AsyncSession, registration_id: int):
    await repository.delete_payment_by_registration_id(db, registration_id)


async def handle_webhook(db: AsyncSession, payload: bytes, stripe_signature: str):
    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, settings.stripe_webhook_secret
        )
    except stripe.SignatureVerificationError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Stripe signature")
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid webhook payload")

    session_id = event["data"]["object"]["id"]

    if event["type"] == "checkout.session.completed":
        payment = await repository.update_payment_status(db, session_id, new_status=PaymentStatusEnum.COMPLETED)
        if payment:
            response = PaymentResponse.model_validate(payment)
            await send_payment_completed(
                response,
                participant_email=payment.participant_email,
                participant_name=payment.participant_name,
            )

    elif event["type"] == "checkout.session.expired":
        payment = await repository.update_payment_status(db, session_id, new_status=PaymentStatusEnum.FAILED)
        if payment:
            response = PaymentResponse.model_validate(payment)
            await send_payment_failed(
                response,
                participant_email=payment.participant_email,
                participant_name=payment.participant_name,
            )

    return {"status": "ok"}