"""Database models for the AI Learning Platform."""
from learning_platform.models.base import Base
from learning_platform.models.user import User, UserProgress
from learning_platform.models.module import LearningModule, ModuleContent, ModuleVersion
from learning_platform.models.assessment import Quiz, QuizQuestion, UserAssessment, AssessmentResult

__all__ = [
    "Base",
    "User",
    "UserProgress",
    "LearningModule",
    "ModuleContent",
    "ModuleVersion",
    "Quiz",
    "QuizQuestion",
    "UserAssessment",
    "AssessmentResult",
]
