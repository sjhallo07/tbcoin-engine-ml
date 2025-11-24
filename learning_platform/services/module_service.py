"""Module service for learning content management."""
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_

from learning_platform.models.module import LearningModule, ModuleContent, ModuleVersion
from learning_platform.schemas.module import (
    LearningModuleCreate,
    LearningModuleUpdate,
    ModuleContentCreate,
    ModuleFilterParams,
)


class ModuleService:
    """Service for learning module operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_module(self, module_data: LearningModuleCreate) -> LearningModule:
        """Create a new learning module."""
        module = LearningModule(
            title=module_data.title,
            slug=module_data.slug,
            description=module_data.description,
            category=module_data.category,
            difficulty_level=module_data.difficulty_level,
            library=module_data.library,
            prerequisites=module_data.prerequisites,
            estimated_duration_minutes=module_data.estimated_duration_minutes,
            topics=module_data.topics,
            learning_objectives=module_data.learning_objectives,
            is_premium=module_data.is_premium,
        )
        
        self.db.add(module)
        self.db.commit()
        self.db.refresh(module)
        return module
    
    def get_module_by_id(self, module_id: int) -> Optional[LearningModule]:
        """Get a module by ID."""
        return self.db.query(LearningModule).filter(LearningModule.id == module_id).first()
    
    def get_module_by_slug(self, slug: str) -> Optional[LearningModule]:
        """Get a module by slug."""
        return self.db.query(LearningModule).filter(LearningModule.slug == slug).first()
    
    def get_all_modules(self, include_unpublished: bool = False) -> List[LearningModule]:
        """Get all learning modules."""
        query = self.db.query(LearningModule)
        if not include_unpublished:
            query = query.filter(LearningModule.is_published == True)
        return query.order_by(LearningModule.order_index).all()
    
    def filter_modules(self, filters: ModuleFilterParams) -> List[LearningModule]:
        """Filter modules based on criteria."""
        query = self.db.query(LearningModule).filter(LearningModule.is_published == True)
        
        if filters.difficulty_level:
            query = query.filter(LearningModule.difficulty_level == filters.difficulty_level)
        
        if filters.library:
            query = query.filter(LearningModule.library == filters.library)
        
        if filters.category:
            query = query.filter(LearningModule.category == filters.category)
        
        if filters.is_premium is not None:
            query = query.filter(LearningModule.is_premium == filters.is_premium)
        
        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.filter(
                or_(
                    LearningModule.title.ilike(search_term),
                    LearningModule.description.ilike(search_term),
                )
            )
        
        return query.order_by(LearningModule.order_index).all()
    
    def get_modules_by_difficulty(self, difficulty_level: str) -> List[LearningModule]:
        """Get modules by difficulty level."""
        return self.db.query(LearningModule).filter(
            LearningModule.difficulty_level == difficulty_level,
            LearningModule.is_published == True
        ).order_by(LearningModule.order_index).all()
    
    def get_modules_by_library(self, library: str) -> List[LearningModule]:
        """Get modules by ML library."""
        return self.db.query(LearningModule).filter(
            LearningModule.library == library,
            LearningModule.is_published == True
        ).order_by(LearningModule.order_index).all()
    
    def update_module(self, module_id: int, module_data: LearningModuleUpdate) -> Optional[LearningModule]:
        """Update a learning module."""
        module = self.get_module_by_id(module_id)
        if not module:
            return None
        
        update_data = module_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(module, field, value)
        
        module.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(module)
        return module
    
    def publish_module(self, module_id: int) -> Optional[LearningModule]:
        """Publish a module."""
        module = self.get_module_by_id(module_id)
        if not module:
            return None
        
        module.is_published = True
        module.published_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(module)
        return module
    
    def add_content(self, module_id: int, content_data: ModuleContentCreate) -> Optional[ModuleContent]:
        """Add content to a module."""
        module = self.get_module_by_id(module_id)
        if not module:
            return None
        
        content = ModuleContent(
            module_id=module_id,
            title=content_data.title,
            content_type=content_data.content_type,
            content_format=content_data.content_format,
            content_body=content_data.content_body,
            content_url=content_data.content_url,
            order_index=content_data.order_index,
            section=content_data.section,
            duration_seconds=content_data.duration_seconds,
            code_language=content_data.code_language,
            code_snippet=content_data.code_snippet,
        )
        
        self.db.add(content)
        self.db.commit()
        self.db.refresh(content)
        return content
    
    def get_module_contents(self, module_id: int) -> List[ModuleContent]:
        """Get all content for a module."""
        return self.db.query(ModuleContent).filter(
            ModuleContent.module_id == module_id,
            ModuleContent.is_published == True
        ).order_by(ModuleContent.order_index).all()
    
    def create_version(self, module_id: int, version_number: str, changelog: str = None) -> Optional[ModuleVersion]:
        """Create a new version of a module."""
        module = self.get_module_by_id(module_id)
        if not module:
            return None
        
        # Set all existing versions to non-current
        self.db.query(ModuleVersion).filter(
            ModuleVersion.module_id == module_id
        ).update({"is_current": False})
        
        # Create snapshot of current content
        contents = self.get_module_contents(module_id)
        content_snapshot = [
            {
                "title": c.title,
                "content_type": c.content_type,
                "content_format": c.content_format,
                "content_body": c.content_body,
                "order_index": c.order_index,
            }
            for c in contents
        ]
        
        version = ModuleVersion(
            module_id=module_id,
            version_number=version_number,
            changelog=changelog,
            content_snapshot=content_snapshot,
            is_current=True,
        )
        
        self.db.add(version)
        module.current_version = version_number
        self.db.commit()
        self.db.refresh(version)
        return version
    
    def get_recommended_modules(self, user_skill_level: str, completed_modules: List[int]) -> List[LearningModule]:
        """Get recommended modules based on user's skill level and progress."""
        # Get modules at user's level that haven't been completed
        query = self.db.query(LearningModule).filter(
            LearningModule.difficulty_level == user_skill_level,
            LearningModule.is_published == True,
            ~LearningModule.id.in_(completed_modules) if completed_modules else True
        )
        
        modules = query.order_by(LearningModule.order_index).limit(5).all()
        
        # If no modules at current level, suggest next level
        if not modules:
            next_level = {"beginner": "intermediate", "intermediate": "advanced"}.get(user_skill_level)
            if next_level:
                modules = self.get_modules_by_difficulty(next_level)[:5]
        
        return modules
