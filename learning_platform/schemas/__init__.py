"""Pydantic schemas for the AI Learning Platform API."""
from learning_platform.schemas.user import UserCreate, UserUpdate, UserResponse, UserProgressResponse
from learning_platform.schemas.module import (
    LearningModuleCreate,
    LearningModuleUpdate,
    LearningModuleResponse,
    ModuleContentCreate,
    ModuleContentResponse,
    ModuleCatalogItem,
)
from learning_platform.schemas.assessment import (
    QuizCreate,
    QuizResponse,
    QuestionCreate,
    QuestionResponse,
    AssessmentSubmission,
    AssessmentResultResponse,
)

__all__ = [
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserProgressResponse",
    "LearningModuleCreate",
    "LearningModuleUpdate",
    "LearningModuleResponse",
    "ModuleContentCreate",
    "ModuleContentResponse",
    "ModuleCatalogItem",
    "QuizCreate",
    "QuizResponse",
    "QuestionCreate",
    "QuestionResponse",
    "AssessmentSubmission",
    "AssessmentResultResponse",
]
