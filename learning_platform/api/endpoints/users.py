"""User management endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from learning_platform.api.dependencies import get_db, require_auth, create_access_token
from learning_platform.models.user import User
from learning_platform.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserProgressResponse,
    UserProgressSummary,
)
from learning_platform.services.user_service import UserService

router = APIRouter()


class LoginRequest:
    """Login request model."""
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    service = UserService(db)
    
    # Check if username or email already exists
    if service.get_user_by_username(user_data.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    if service.get_user_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user = service.create_user(user_data)
    return user


@router.post("/login")
async def login(username: str, password: str, db: Session = Depends(get_db)):
    """Authenticate and get access token."""
    service = UserService(db)
    user = service.authenticate_user(username, password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    token = create_access_token(user.id)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "skill_level": user.skill_level
        }
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(require_auth)):
    """Get current user's profile."""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_data: UserUpdate,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Update current user's profile."""
    service = UserService(db)
    updated_user = service.update_user(current_user.id, user_data)
    return updated_user


@router.get("/me/progress", response_model=List[UserProgressResponse])
async def get_my_progress(
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get current user's learning progress."""
    service = UserService(db)
    progress = service.get_user_progress(current_user.id)
    return progress


@router.get("/me/summary", response_model=UserProgressSummary)
async def get_my_progress_summary(
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get summary of current user's learning progress."""
    service = UserService(db)
    summary = service.get_progress_summary(current_user.id)
    return summary
