"""Learning module models for course content organization."""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Boolean, Text, JSON
from sqlalchemy.orm import relationship

from learning_platform.models.base import Base


class LearningModule(Base):
    """Learning module model containing course information."""
    
    __tablename__ = "learning_modules"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Categorization
    category = Column(String(50), nullable=False, index=True)  # ml-basics, deep-learning, etc.
    difficulty_level = Column(String(20), nullable=False, index=True)  # beginner, intermediate, advanced
    library = Column(String(50), nullable=True, index=True)  # scikit-learn, tensorflow, pytorch, xgboost, lightgbm
    
    # Prerequisites (stored as JSON list of module IDs or slugs)
    prerequisites = Column(JSON, default=list)
    
    # Module metadata
    estimated_duration_minutes = Column(Integer, default=60)
    topics = Column(JSON, default=list)  # List of topic tags
    learning_objectives = Column(JSON, default=list)  # List of learning objectives
    
    # Status
    is_published = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    order_index = Column(Integer, default=0)  # For ordering within a category
    
    # Version control
    current_version = Column(String(20), default="1.0.0")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
    
    # Relationships
    contents = relationship("ModuleContent", back_populates="module", cascade="all, delete-orphan")
    versions = relationship("ModuleVersion", back_populates="module", cascade="all, delete-orphan")
    user_progress = relationship("UserProgress", back_populates="module", cascade="all, delete-orphan")
    quizzes = relationship("Quiz", back_populates="module", cascade="all, delete-orphan")


class ModuleContent(Base):
    """Content items within a learning module."""
    
    __tablename__ = "module_contents"
    
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("learning_modules.id"), nullable=False, index=True)
    
    # Content details
    title = Column(String(255), nullable=False)
    content_type = Column(String(20), nullable=False)  # text, video, code, quiz
    content_format = Column(String(20), default="markdown")  # markdown, html, jupyter
    
    # Content body (for text/markdown) or reference (for video URL)
    content_body = Column(Text, nullable=True)
    content_url = Column(String(500), nullable=True)  # For videos or external resources
    
    # Ordering and navigation
    order_index = Column(Integer, default=0)
    section = Column(String(100), nullable=True)  # Section/chapter name
    
    # Duration for videos (in seconds)
    duration_seconds = Column(Integer, nullable=True)
    
    # Code examples
    code_language = Column(String(20), nullable=True)  # python, jupyter
    code_snippet = Column(Text, nullable=True)
    
    # Status
    is_published = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    module = relationship("LearningModule", back_populates="contents")


class ModuleVersion(Base):
    """Version history for learning modules."""
    
    __tablename__ = "module_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("learning_modules.id"), nullable=False, index=True)
    
    # Version info
    version_number = Column(String(20), nullable=False)
    changelog = Column(Text, nullable=True)
    
    # Content snapshot (JSON backup of contents at this version)
    content_snapshot = Column(JSON, nullable=True)
    
    # Status
    is_current = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, nullable=True)  # User ID who created this version
    
    # Relationships
    module = relationship("LearningModule", back_populates="versions")
