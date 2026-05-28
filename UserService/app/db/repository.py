from sqlalchemy.orm import selectinload
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.schema import ParticipantCreate, OrganiserCreate, AdminCreate
from app.db.models import User, Participant, Organiser, Admin

async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(
        select(User)
        .options(
            selectinload(User.admin),
            selectinload(User.participant),
            selectinload(User.organiser)
        )
    .where(User.email == email)
    )
    return result.scalar_one_or_none()

async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    result = await db.execute(
        select(User)
        .options(
            selectinload(User.admin),
            selectinload(User.participant),
            selectinload(User.organiser)
        )
    .where(User.id == user_id)
    )
    return result.scalar_one_or_none()

async def create_participant(db: AsyncSession, data: ParticipantCreate, password_hash: str) -> User:
    try:
        user_model = User(
            email=data.email,
            password_hash=password_hash,
            first_name=data.first_name,
            last_name=data.last_name
        )
        participant_model = Participant(
            date_of_birth=data.date_of_birth,
            gender=data.gender,
            tshirt_size=data.tshirt_size,
            emergency_contact=data.emergency_contact
        )
        user_model.participant = participant_model

        db.add(user_model)
        await db.commit()
        result = await db.execute(
            select(User)
            .options(
                selectinload(User.participant),
                selectinload(User.organiser),
                selectinload(User.admin)
            )
            .where(User.id == user_model.id)
        )
        return result.scalar_one()
    except Exception as e:
        await db.rollback()
        raise e
    
async def create_organiser(db: AsyncSession, data: OrganiserCreate, password_hash: str) -> User:
    try:
        user_model = User(
            email=data.email,
            password_hash=password_hash,
            first_name=data.first_name,
            last_name=data.last_name
        )
        organiser_model = Organiser(
            organization_name=data.organization_name,
            website=str(data.website) if data.website else None,
            description=data.description
        )
        user_model.organiser = organiser_model
        
        db.add(user_model)
        await db.commit()
        result = await db.execute(
            select(User)
            .options(
                selectinload(User.participant),
                selectinload(User.organiser),
                selectinload(User.admin)
            )
            .where(User.id == user_model.id)
        )
        return result.scalar_one()
    except Exception as e:
        await db.rollback()
        raise e
    
async def create_admin(db: AsyncSession, user_id: int, admin_level: int = 1) -> User:
    try:
        admin_model = Admin(
            id=user_id,
            admin_level=admin_level
        )
        db.add(admin_model)
        await db.commit()
        result = await db.execute(
            select(User)
            .options(
                selectinload(User.participant),
                selectinload(User.organiser),
                selectinload(User.admin)
            )
            .where(User.id == user_id)
        )
        return result.scalar_one()
    except Exception as e:
        await db.rollback()
        raise e