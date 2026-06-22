from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.model import Payment
from app.enum import PaymentStatusEnum as PaymentStatus


async def get_payment_by_id(db: AsyncSession, payment_id: int):
    result = await db.execute(select(Payment).where(Payment.id == payment_id))
    return result.scalar_one_or_none()


async def get_payment_by_stripe_session_id(db: AsyncSession, stripe_session_id: str):
    result = await db.execute(
        select(Payment).where(Payment.stripe_session_id == stripe_session_id)
    )
    return result.scalar_one_or_none()


async def get_payments_by_user_id(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(Payment).where(Payment.user_id == user_id)
    )
    return result.scalars().all()


async def get_payment_by_registration_id(db: AsyncSession, registration_id: int):
    result = await db.execute(
        select(Payment).where(Payment.registration_id == registration_id)
    )
    return result.scalar_one_or_none()


async def create_payment(
    db: AsyncSession,
    user_id: int,
    registration_id: int,
    stripe_session_id: str,
    amount: float,
    participant_email: str,
    participant_name: str,
    checkout_url: str | None = None,
):
    payment = Payment(
        user_id=user_id,
        registration_id=registration_id,
        stripe_session_id=stripe_session_id,
        amount=amount,
        status=PaymentStatus.PENDING,
        checkout_url=checkout_url,
        participant_email=participant_email,
        participant_name=participant_name,
    )
    db.add(payment)
    await db.commit()
    await db.refresh(payment)
    return payment


async def update_payment_status(
    db: AsyncSession,
    stripe_session_id: str,
    new_status: PaymentStatus,
):
    payment = await get_payment_by_stripe_session_id(db, stripe_session_id)
    if not payment or payment.status == new_status:
        return payment
    payment.status = new_status
    await db.commit()
    await db.refresh(payment)
    return payment


async def delete_payment_by_registration_id(db: AsyncSession, registration_id: int):
    result = await db.execute(
        select(Payment).where(Payment.registration_id == registration_id)
    )
    payment = result.scalar_one_or_none()
    if payment:
        await db.delete(payment)
        await db.commit()