from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status
from app.db.db import get_db
from app.api.schema import ParticipantCreate, OrganiserCreate, UserResponse, TokenResponse, LoginRequest
import app.service as service
router = APIRouter(prefix="/api/users/auth", tags=["auth"])

@router.post("/register/participant", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_participant(data: ParticipantCreate, db: AsyncSession = Depends(get_db)):
    return await service.register_participant(db, data)

@router.post("/register/organiser", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_organiser(data: OrganiserCreate, db: AsyncSession = Depends(get_db)):
    return await service.register_organiser(db, data)

@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await service.login(db, data.email, data.password)