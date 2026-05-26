from fastapi import APIRouter

router = APIRouter(prefix="/api/users/auth", tags=["Auth"])

@router.post("/login")
def login(username: str, password: str):
    if username == "admin" and password == "password":
        return {"message": "Login successful", "token": "fake-jwt-token"}
    return {"message": "Invalid credentials"}