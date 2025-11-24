"""Learning module Pydantic schemas."""
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, ConfigDict, Field


class ModuleContentCreate(BaseModel):
    """Schema for creating module content."""
    title: str = Field(..., max_length=255)
    content_type: str = Field(..., pattern="^(text|video|code|quiz)$")
    content_format: str = Field(default="markdown", pattern="^(markdown|html|jupyter)$")
    content_body: Optional[str] = None
    content_url: Optional[str] = None
    order_index: int = Field(default=0)
    section: Optional[str] = None
    duration_seconds: Optional[int] = None
    code_language: Optional[str] = None
    code_snippet: Optional[str] = None


class ModuleContentResponse(BaseModel):
    """Schema for module content response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    module_id: int
    title: str
    content_type: str
    content_format: str
    content_body: Optional[str] = None
    content_url: Optional[str] = None
    order_index: int
    section: Optional[str] = None
    duration_seconds: Optional[int] = None
    code_language: Optional[str] = None
    code_snippet: Optional[str] = None
    is_published: bool
    created_at: datetime
    updated_at: datetime


class LearningModuleCreate(BaseModel):
    """Schema for creating a learning module."""
    title: str = Field(..., max_length=255)
    slug: str = Field(..., max_length=255, pattern="^[a-z0-9-]+$")
    description: Optional[str] = None
    category: str = Field(..., max_length=50)
    difficulty_level: str = Field(..., pattern="^(beginner|intermediate|advanced)$")
    library: Optional[str] = None
    prerequisites: List[str] = Field(default_factory=list)
    estimated_duration_minutes: int = Field(default=60, ge=1)
    topics: List[str] = Field(default_factory=list)
    learning_objectives: List[str] = Field(default_factory=list)
    is_premium: bool = False


class LearningModuleUpdate(BaseModel):
    """Schema for updating a learning module."""
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = None
    difficulty_level: Optional[str] = Field(None, pattern="^(beginner|intermediate|advanced)$")
    library: Optional[str] = None
    prerequisites: Optional[List[str]] = None
    estimated_duration_minutes: Optional[int] = Field(None, ge=1)
    topics: Optional[List[str]] = None
    learning_objectives: Optional[List[str]] = None
    is_published: Optional[bool] = None
    is_premium: Optional[bool] = None


class LearningModuleResponse(BaseModel):
    """Schema for learning module response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    slug: str
    description: Optional[str] = None
    category: str
    difficulty_level: str
    library: Optional[str] = None
    prerequisites: List[str] = Field(default_factory=list)
    estimated_duration_minutes: int
    topics: List[str] = Field(default_factory=list)
    learning_objectives: List[str] = Field(default_factory=list)
    is_published: bool
    is_premium: bool
    current_version: str
    order_index: int
    created_at: datetime
    updated_at: datetime
    contents: List[ModuleContentResponse] = Field(default_factory=list)


class ModuleCatalogItem(BaseModel):
    """Lightweight schema for module catalog listing."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    slug: str
    description: Optional[str] = None
    category: str
    difficulty_level: str
    library: Optional[str] = None
    estimated_duration_minutes: int
    topics: List[str] = Field(default_factory=list)
    is_premium: bool
    order_index: int


class ModuleFilterParams(BaseModel):
    """Parameters for filtering modules."""
    difficulty_level: Optional[str] = None
    library: Optional[str] = None
    category: Optional[str] = None
    topics: Optional[List[str]] = None
    is_premium: Optional[bool] = None
    search: Optional[str] = None
