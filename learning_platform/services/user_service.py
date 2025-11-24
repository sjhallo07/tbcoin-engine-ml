"""User service for authentication and user management."""
import hashlib
import secrets
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session

from learning_platform.models.user import User, UserProgress
from learning_platform.schemas.user import UserCreate, UserUpdate


class UserService:
    """Service for user-related operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using SHA-256 with salt."""
        salt = secrets.token_hex(16)
        hashed = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}${hashed}"
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        try:
            salt, stored_hash = hashed_password.split("$")
            computed_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return computed_hash == stored_hash
        except ValueError:
            return False
    
    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        hashed_password = self.hash_password(user_data.password)
        
        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            skill_level=user_data.skill_level,
            preferred_library=user_data.preferred_library,
            learning_goals=user_data.learning_goals,
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get a user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by username."""
        return self.db.query(User).filter(User.username == username).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email."""
        return self.db.query(User).filter(User.email == email).first()
    
    def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update a user's profile."""
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user with username and password."""
        user = self.get_user_by_username(username)
        if not user:
            return None
        
        if not self.verify_password(password, user.hashed_password):
            return None
        
        user.last_login = datetime.utcnow()
        self.db.commit()
        return user
    
    def get_user_progress(self, user_id: int) -> List[UserProgress]:
        """Get all progress records for a user."""
        return self.db.query(UserProgress).filter(
            UserProgress.user_id == user_id
        ).all()
    
    def get_user_module_progress(self, user_id: int, module_id: int) -> Optional[UserProgress]:
        """Get user's progress for a specific module."""
        return self.db.query(UserProgress).filter(
            UserProgress.user_id == user_id,
            UserProgress.module_id == module_id
        ).first()
    
    def update_module_progress(
        self,
        user_id: int,
        module_id: int,
        completion_percentage: float,
        time_spent_minutes: int = 0,
        last_content_id: Optional[int] = None,
    ) -> UserProgress:
        """Update or create user progress for a module."""
        progress = self.get_user_module_progress(user_id, module_id)
        
        if not progress:
            progress = UserProgress(
                user_id=user_id,
                module_id=module_id,
                completion_percentage=completion_percentage,
                time_spent_minutes=time_spent_minutes,
                last_content_id=last_content_id,
            )
            self.db.add(progress)
        else:
            progress.completion_percentage = completion_percentage
            progress.time_spent_minutes += time_spent_minutes
            if last_content_id:
                progress.last_content_id = last_content_id
            progress.last_accessed = datetime.utcnow()
        
        if completion_percentage >= 100:
            progress.is_completed = True
            progress.completed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(progress)
        return progress
    
    def get_progress_summary(self, user_id: int) -> dict:
        """Get a summary of user's overall progress."""
        progress_list = self.get_user_progress(user_id)
        
        total_started = len(progress_list)
        total_completed = sum(1 for p in progress_list if p.is_completed)
        total_time = sum(p.time_spent_minutes for p in progress_list)
        
        quiz_scores = [p.quiz_average_score for p in progress_list if p.quiz_average_score is not None]
        avg_quiz_score = sum(quiz_scores) / len(quiz_scores) if quiz_scores else None
        
        user = self.get_user_by_id(user_id)
        
        return {
            "total_modules_started": total_started,
            "total_modules_completed": total_completed,
            "total_time_spent_minutes": total_time,
            "average_quiz_score": avg_quiz_score,
            "current_skill_level": user.skill_level if user else "beginner",
        }
