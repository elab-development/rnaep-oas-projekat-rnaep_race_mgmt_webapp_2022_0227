import secrets

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status
from app.db.db import get_db
from app.api.schema import ParticipantCreate, OrganiserCreate, UserResponse, LoginRequest
import app.service as service
from app.config import settings
from app.core.auth import verify_token

#AUTH ROUTES#
auth_router = APIRouter(prefix="/api/users/auth", tags=["Auth"])

@auth_router.post("/register/participant", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_participant(data: ParticipantCreate, db: AsyncSession = Depends(get_db)):
    return await service.register_participant(db, data)

@auth_router.post("/register/organiser", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_organiser(data: OrganiserCreate, db: AsyncSession = Depends(get_db)):
    return await service.register_organiser(db, data)

@auth_router.post("/login")
async def login(data: LoginRequest, response: Response ,db: AsyncSession = Depends(get_db)):
    result = await service.login(db, data.email, data.password)
    response.set_cookie(
        key="access_token",
        value=result,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        max_age=60 * 60 * 24 * settings.access_token_expire_days
    )
    # Double-submit CSRF cookie: deliberately NOT httponly, so the frontend can
    # read it and echo it back as the X-CSRF-Token header on state-changing
    # requests. An attacker's cross-site page can't read this cookie (browser
    # same-origin policy), so it can't forge the matching header.
    response.set_cookie(
        key="csrf_token",
        value=secrets.token_urlsafe(32),
        httponly=False,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        max_age=60 * 60 * 24 * settings.access_token_expire_days
    )
    return {"message": "Login successful"}


@auth_router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="csrf_token")
    return {"message": "Logout successful"}

#CLASSIC USER ROUTES#
user_router = APIRouter(prefix="/api/users", tags=["Users"])
@user_router.get("/me")
async def get_my_profile(request: Request, db: AsyncSession = Depends(get_db)):
    access_token = request.cookies.get("access_token")
    payload = verify_token(access_token) if access_token else None
    user_id = payload.get("sub") if payload else None
    return await service.get_me(db, user_id)