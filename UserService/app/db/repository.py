from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.schema import ParticipantCreate, OrganiserCreate, AdminCreate
from app.db.models import User, Participant, Organiser, Admin

async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()

async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
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
        await db.refresh(user_model)
        return user_model
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
        await db.refresh(user_model)
        return user_model
    except Exception as e:
        await db.rollback()
        raise e
    
async def create_admin(db: AsyncSession, data: AdminCreate, password_hash: str) -> User:
    try:
        user_model = User(
            email=data.email,
            password_hash=password_hash,
            first_name=data.first_name,
            last_name=data.last_name
        )
        admin_model = Admin(
            admin_level=data.admin_level
        )
        user_model.admin = admin_model
        
        db.add(user_model)
        await db.commit()
        await db.refresh(user_model)
        return user_model
    except Exception as e:
        await db.rollback()
        raise e