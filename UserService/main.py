from fastapi import FastAPI, HTTPException, Depends
from UserService.app.api.router import router as auth_router

app = FastAPI()

app.include_router(auth_router)

