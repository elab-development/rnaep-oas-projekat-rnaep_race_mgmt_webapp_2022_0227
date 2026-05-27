from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.api.schema import ParticipantCreate, OrganiserCreate
from app.db import repository
from app.core.auth import hash_password, verify_password, create_access_token
#----#
def get_user_role(user) -> str:
    if user.admin:
        return "admin"
    if user.organiser:
        return "organiser"
    if user.participant:
        return "participant"
    return "user"
#----#

async def register_participant(db: AsyncSession, data: ParticipantCreate):
    if await repository.get_user_by_email(db, data.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    password_hash = hash_password(data.password)
    return await repository.create_participant(db, data, password_hash)

async def register_organiser(db: AsyncSession, data: OrganiserCreate):
    if await repository.get_user_by_email(db, data.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    password_hash = hash_password(data.password)
    return await repository.create_organiser(db, data, password_hash)

async def login(db: AsyncSession, email: str, password: str):
    user = await repository.get_user_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")
    return create_access_token({
        "sub": str(user.id),
        "email": user.email,
        "role": get_user_role(user)
    })


#USERS FUNCTIONS#
async def get_me(db: AsyncSession, user_id: str):
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    user = await repository.get_user_by_id(db, int(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


#ADMIN FUNCTIONS#
async def promote_to_admin(db: AsyncSession, user_id: int, admin_level: int = 1):
    user = await repository.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.admin:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is already an admin")
    return await repository.create_admin(db, user_id, admin_level)