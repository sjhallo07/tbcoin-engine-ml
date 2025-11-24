"""Learning module endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from learning_platform.api.dependencies import get_db, get_current_user
from learning_platform.models.user import User
from learning_platform.schemas.module import (
    LearningModuleCreate,
    LearningModuleUpdate,
    LearningModuleResponse,
    ModuleContentCreate,
    ModuleContentResponse,
    ModuleCatalogItem,
    ModuleFilterParams,
)
from learning_platform.services.module_service import ModuleService

router = APIRouter()


@router.get("/", response_model=List[ModuleCatalogItem])
async def list_modules(
    difficulty_level: Optional[str] = Query(None, pattern="^(beginner|intermediate|advanced)$"),
    library: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all published learning modules with optional filtering."""
    service = ModuleService(db)
    
    if any([difficulty_level, library, category, search]):
        filters = ModuleFilterParams(
            difficulty_level=difficulty_level,
            library=library,
            category=category,
            search=search
        )
        modules = service.filter_modules(filters)
    else:
        modules = service.get_all_modules()
    
    return modules


@router.get("/by-difficulty/{difficulty_level}", response_model=List[ModuleCatalogItem])
async def get_modules_by_difficulty(
    difficulty_level: str,
    db: Session = Depends(get_db)
):
    """Get modules by difficulty level."""
    if difficulty_level not in ["beginner", "intermediate", "advanced"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid difficulty level"
        )
    
    service = ModuleService(db)
    modules = service.get_modules_by_difficulty(difficulty_level)
    return modules


@router.get("/by-library/{library}", response_model=List[ModuleCatalogItem])
async def get_modules_by_library(
    library: str,
    db: Session = Depends(get_db)
):
    """Get modules by ML library."""
    service = ModuleService(db)
    modules = service.get_modules_by_library(library)
    return modules


@router.get("/recommended", response_model=List[ModuleCatalogItem])
async def get_recommended_modules(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recommended modules for the current user."""
    service = ModuleService(db)
    
    skill_level = current_user.skill_level if current_user else "beginner"
    completed = []
    
    if current_user:
        from learning_platform.models.user import UserProgress
        progress = db.query(UserProgress).filter(
            UserProgress.user_id == current_user.id,
            UserProgress.is_completed == True
        ).all()
        completed = [p.module_id for p in progress]
    
    modules = service.get_recommended_modules(skill_level, completed)
    return modules


@router.get("/{slug}", response_model=LearningModuleResponse)
async def get_module(slug: str, db: Session = Depends(get_db)):
    """Get a specific module by slug."""
    service = ModuleService(db)
    module = service.get_module_by_slug(slug)
    
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    return module


@router.get("/{slug}/contents", response_model=List[ModuleContentResponse])
async def get_module_contents(slug: str, db: Session = Depends(get_db)):
    """Get all content for a module."""
    service = ModuleService(db)
    module = service.get_module_by_slug(slug)
    
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    contents = service.get_module_contents(module.id)
    return contents


@router.post("/", response_model=LearningModuleResponse, status_code=status.HTTP_201_CREATED)
async def create_module(
    module_data: LearningModuleCreate,
    db: Session = Depends(get_db)
):
    """Create a new learning module (admin only)."""
    service = ModuleService(db)
    
    # Check if slug already exists
    existing = service.get_module_by_slug(module_data.slug)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Module with this slug already exists"
        )
    
    module = service.create_module(module_data)
    return module


@router.put("/{slug}", response_model=LearningModuleResponse)
async def update_module(
    slug: str,
    module_data: LearningModuleUpdate,
    db: Session = Depends(get_db)
):
    """Update a learning module (admin only)."""
    service = ModuleService(db)
    module = service.get_module_by_slug(slug)
    
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    updated = service.update_module(module.id, module_data)
    return updated


@router.post("/{slug}/contents", response_model=ModuleContentResponse, status_code=status.HTTP_201_CREATED)
async def add_module_content(
    slug: str,
    content_data: ModuleContentCreate,
    db: Session = Depends(get_db)
):
    """Add content to a module (admin only)."""
    service = ModuleService(db)
    module = service.get_module_by_slug(slug)
    
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    content = service.add_content(module.id, content_data)
    return content


@router.post("/{slug}/publish", response_model=LearningModuleResponse)
async def publish_module(slug: str, db: Session = Depends(get_db)):
    """Publish a module (admin only)."""
    service = ModuleService(db)
    module = service.get_module_by_slug(slug)
    
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    published = service.publish_module(module.id)
    return published


@router.post("/{slug}/version", status_code=status.HTTP_201_CREATED)
async def create_module_version(
    slug: str,
    version_number: str,
    changelog: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Create a new version of a module (admin only)."""
    service = ModuleService(db)
    module = service.get_module_by_slug(slug)
    
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    version = service.create_version(module.id, version_number, changelog)
    return {"message": "Version created", "version": version_number}
