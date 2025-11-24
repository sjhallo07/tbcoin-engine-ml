"""User-related Pydantic schemas."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = Field(None, max_length=100)
    skill_level: str = Field(default="beginner", pattern="^(beginner|intermediate|advanced)$")
    preferred_library: Optional[str] = None
    learning_goals: Optional[str] = None


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    full_name: Optional[str] = Field(None, max_length=100)
    skill_level: Optional[str] = Field(None, pattern="^(beginner|intermediate|advanced)$")
    preferred_library: Optional[str] = None
    learning_goals: Optional[str] = None


class UserResponse(BaseModel):
    """Schema for user response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    skill_level: str
    preferred_library: Optional[str] = None
    learning_goals: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None


class UserProgressResponse(BaseModel):
    """Schema for user progress response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    module_id: int
    module_title: Optional[str] = None
    completion_percentage: float
    is_completed: bool
    time_spent_minutes: int
    quiz_average_score: Optional[float] = None
    exercises_completed: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    last_accessed: Optional[datetime] = None


class UserProgressSummary(BaseModel):
    """Summary of user's overall progress."""
    total_modules_started: int
    total_modules_completed: int
    total_time_spent_minutes: int
    average_quiz_score: Optional[float] = None
    current_skill_level: str
    recommended_next_module: Optional[str] = None
