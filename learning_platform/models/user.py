"""User models for authentication and progress tracking."""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship

from learning_platform.models.base import Base


class User(Base):
    """User profile model for learners."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    
    # Profile settings
    skill_level = Column(String(20), default="beginner")  # beginner, intermediate, advanced
    preferred_library = Column(String(50), nullable=True)  # scikit-learn, tensorflow, pytorch
    learning_goals = Column(Text, nullable=True)
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    progress = relationship("UserProgress", back_populates="user", cascade="all, delete-orphan")
    assessments = relationship("UserAssessment", back_populates="user", cascade="all, delete-orphan")


class UserProgress(Base):
    """Track user progress through learning modules."""
    
    __tablename__ = "user_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    module_id = Column(Integer, ForeignKey("learning_modules.id"), nullable=False, index=True)
    
    # Progress tracking
    completion_percentage = Column(Float, default=0.0)
    is_completed = Column(Boolean, default=False)
    time_spent_minutes = Column(Integer, default=0)
    
    # Last position
    last_content_id = Column(Integer, nullable=True)
    last_position = Column(Integer, default=0)  # For video/text position
    
    # Performance metrics
    quiz_average_score = Column(Float, nullable=True)
    exercises_completed = Column(Integer, default=0)
    
    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    last_accessed = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="progress")
    module = relationship("LearningModule", back_populates="user_progress")
