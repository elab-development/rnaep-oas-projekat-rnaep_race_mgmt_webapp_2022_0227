from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status
from app.db.db import get_db
from app.api.schema import ParticipantCreate, OrganiserCreate, UserResponse, TokenResponse, LoginRequest
import app.service as service
from app.config import settings

#AUTH ROUTES#
router = APIRouter(prefix="/api/users/auth", tags=["auth"])

@router.post("/register/participant", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_participant(data: ParticipantCreate, db: AsyncSession = Depends(get_db)):
    return await service.register_participant(db, data)

@router.post("/register/organiser", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_organiser(data: OrganiserCreate, db: AsyncSession = Depends(get_db)):
    return await service.register_organiser(db, data)

@router.post("/login")
async def login(data: LoginRequest, response: Response ,db: AsyncSession = Depends(get_db)):
    result = await service.login(db, data.email, data.password)
    response.set_cookie(
        key="access_token",
        value=result["access_token"],
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=60 * 60 * 24 * settings.access_token_expire_days
    )
    return {"message": "Login successful"}


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Logout successful"}