"""Progress tracking endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from learning_platform.api.dependencies import get_db, require_auth
from learning_platform.models.user import User
from learning_platform.schemas.user import UserProgressResponse
from learning_platform.services.user_service import UserService
from learning_platform.services.module_service import ModuleService
from learning_platform.services.adaptive_learning_service import AdaptiveLearningService

router = APIRouter()


@router.post("/module/{module_slug}/update")
async def update_module_progress(
    module_slug: str,
    completion_percentage: float,
    time_spent_minutes: int = 0,
    last_content_id: Optional[int] = None,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Update progress for a module."""
    module_service = ModuleService(db)
    module = module_service.get_module_by_slug(module_slug)
    
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    user_service = UserService(db)
    progress = user_service.update_module_progress(
        current_user.id,
        module.id,
        completion_percentage,
        time_spent_minutes,
        last_content_id
    )
    
    return {
        "message": "Progress updated",
        "completion_percentage": progress.completion_percentage,
        "is_completed": progress.is_completed
    }


@router.get("/module/{module_slug}", response_model=UserProgressResponse)
async def get_module_progress(
    module_slug: str,
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get progress for a specific module."""
    module_service = ModuleService(db)
    module = module_service.get_module_by_slug(module_slug)
    
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    user_service = UserService(db)
    progress = user_service.get_user_module_progress(current_user.id, module.id)
    
    if not progress:
        # Return empty progress
        return UserProgressResponse(
            id=0,
            user_id=current_user.id,
            module_id=module.id,
            module_title=module.title,
            completion_percentage=0.0,
            is_completed=False,
            time_spent_minutes=0,
            quiz_average_score=None,
            exercises_completed=0,
            started_at=None,
            completed_at=None,
            last_accessed=None
        )
    
    return UserProgressResponse(
        id=progress.id,
        user_id=progress.user_id,
        module_id=progress.module_id,
        module_title=module.title,
        completion_percentage=progress.completion_percentage,
        is_completed=progress.is_completed,
        time_spent_minutes=progress.time_spent_minutes,
        quiz_average_score=progress.quiz_average_score,
        exercises_completed=progress.exercises_completed,
        started_at=progress.started_at,
        completed_at=progress.completed_at,
        last_accessed=progress.last_accessed
    )


@router.get("/next-module")
async def get_next_recommended_module(
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get the next recommended module for the user."""
    adaptive_service = AdaptiveLearningService(db)
    next_module = adaptive_service.suggest_next_module(current_user.id)
    
    if not next_module:
        return {"message": "Congratulations! You've completed all available modules."}
    
    module_service = ModuleService(db)
    module = module_service.get_module_by_slug(next_module)
    
    return {
        "recommended_module": {
            "slug": module.slug,
            "title": module.title,
            "difficulty_level": module.difficulty_level,
            "library": module.library,
            "estimated_duration_minutes": module.estimated_duration_minutes
        }
    }


@router.get("/skill-progression")
async def get_skill_progression(
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get user's skill progression over time."""
    adaptive_service = AdaptiveLearningService(db)
    progression = adaptive_service.calculate_skill_progression(current_user.id)
    return progression


@router.post("/level-up")
async def request_level_up(
    current_user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Request a skill level upgrade based on performance."""
    adaptive_service = AdaptiveLearningService(db)
    progression = adaptive_service.calculate_skill_progression(current_user.id)
    
    if not progression.get("ready_for_level_upgrade"):
        return {
            "success": False,
            "message": "Not ready for level upgrade yet. Complete more modules and maintain high quiz scores.",
            "current_level": progression.get("current_level"),
            "average_score": progression.get("average_recent_score"),
            "modules_completed": progression.get("total_modules_completed")
        }
    
    # Upgrade level
    level_order = {"beginner": "intermediate", "intermediate": "advanced", "advanced": "advanced"}
    new_level = level_order.get(current_user.skill_level, "beginner")
    
    if new_level == current_user.skill_level:
        return {
            "success": False,
            "message": "You're already at the highest level!",
            "current_level": current_user.skill_level
        }
    
    # Update user level
    current_user.skill_level = new_level
    db.commit()
    
    return {
        "success": True,
        "message": f"Congratulations! You've been upgraded to {new_level} level!",
        "new_level": new_level
    }
