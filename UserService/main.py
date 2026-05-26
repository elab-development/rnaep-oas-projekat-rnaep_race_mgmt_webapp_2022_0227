from fastapi import FastAPI, HTTPException, Depends
from app.routes.auth import router as auth_router

app = FastAPI()

app.include_router(auth_router)

