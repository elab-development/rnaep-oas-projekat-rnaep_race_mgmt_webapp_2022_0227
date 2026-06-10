from fastapi import Request, HTTPException, status, Depends
from app.core.auth import verify_token

def get_current_user(request: Request) -> dict:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    return payload  

def require_organiser(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user.get("role") not in ("organiser", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organisers can perform this action"
        )
    return current_user

def require_participant(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user.get("role") not in ("participant", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only participants can perform this action"
        )
    return current_user