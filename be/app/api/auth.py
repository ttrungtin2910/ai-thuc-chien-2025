"""
Authentication API Routes
"""

from fastapi import APIRouter, HTTPException, Depends
from datetime import timedelta

from ..models.auth import LoginRequest, LoginResponse, UserInfo
from ..core.security import authenticate_user, create_access_token, verify_token, get_user
from ..core.config import Config

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """User login endpoint"""
    user = authenticate_user(request.username, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token = create_access_token(
        data={"sub": request.username},
        expires_delta=timedelta(hours=Config.ACCESS_TOKEN_EXPIRE_HOURS)
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user_info={
            "username": user["username"],
            "full_name": user["full_name"],
            "role": user["role"]
        }
    )


@router.get("/me", response_model=UserInfo)
async def get_current_user(username: str = Depends(verify_token)):
    """Get current user information"""
    user = get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserInfo(
        username=user["username"],
        full_name=user["full_name"],
        role=user["role"]
    )
