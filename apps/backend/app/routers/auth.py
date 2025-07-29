from fastapi import HTTPException, APIRouter, status
from ..models import LoginRequest, TokenResponse
from ..dependencies import create_token, USERS

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest):
    user = USERS.get(data.username)
    if not user or user["password"] != data.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_token(data.username)
    return {"token": token}
