import random
import string
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.enum import PaymentStatusEnum
from app.api.schema import RegistrationCreate
from app.db.models import  Registration

#Registration repository functions

async def get_registration_by_id(db: AsyncSession, registration_id: int) -> Registration | None:
    result = await db.execute(
        select(Registration).where(Registration.id == registration_id)
    )
    return result.scalar_one_or_none()

async def get_registrations_by_race_id(db: AsyncSession, race_id: int) -> list[Registration]:
    result = await db.execute(
        select(Registration).where(
            and_(
                Registration.race_id == race_id,
            )
        )
    )
    return result.scalars().all() 

async def get_registrations_by_participant_id(db: AsyncSession, participant_id: int) -> list[Registration]:
    result = await db.execute(
        select(Registration).where(Registration.participant_id == participant_id)    
    )
    return result.scalars().all()

async def get_registration_by_participant_and_race(db: AsyncSession, participant_id: int, race_id: int):
    result = await db.execute(
        select(Registration).where(
            and_(
                Registration.participant_id == participant_id,
                Registration.race_id == race_id
            )
        )
    )
    return result.scalar_one_or_none()
    
async def get_registration_count_by_race(db, race_id):
    result = await db.execute(
        select(func.count()).where(
            and_(
                Registration.race_id == race_id,
                Registration.payment_status != PaymentStatusEnum.PENDING,
                Registration.payment_status != PaymentStatusEnum.FAILED
            )
        )
    )
    return result.scalar()
    
async def create_registration(db: AsyncSession, participant_id: int, race_id: int, data: RegistrationCreate) -> Registration | None:
    bib_number = await generate_unique_bib_number(db, race_id)
    registration_model = Registration(
        participant_id=participant_id,
        race_id=race_id,
        payment_status=PaymentStatusEnum.PENDING,
        bib_number=bib_number
    )
    db.add(registration_model)
    await db.flush()
    return registration_model

async def delete_registration(db: AsyncSession, registration_id: int) -> bool:
    try:
        registration = await get_registration_by_id(db, registration_id)
        if not registration:
            return False
        await db.delete(registration)
        await db.commit()
        return True
    except Exception as e:
        await db.rollback()
        raise e
    
async def update_registration_payment_status(db: AsyncSession, registration_id: int, status: PaymentStatusEnum):
    try:
        registration = await get_registration_by_id(db, registration_id)
        if not registration:
            return None
        registration.payment_status = status
        await db.commit()
        await db.refresh(registration)
        return registration
    except Exception as e:
        await db.rollback()
        raise e
    

# additional functions

async def generate_unique_bib_number(db: AsyncSession, race_id: int, length: int = 6) -> str:
    max_attempts = 10
    for _ in range(max_attempts):
        bib_number = ''.join(random.choices(string.digits, k=length))
        result = await db.execute(
            select(Registration).where(
                and_(
                    Registration.race_id == race_id,
                    Registration.bib_number == bib_number
                )
            )
        )
        if result.scalar_one_or_none() is None:
            return bib_number
    raise ValueError("Error while generating bib_number!")