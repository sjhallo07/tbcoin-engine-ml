"""Services for the AI Learning Platform."""
from learning_platform.services.user_service import UserService
from learning_platform.services.module_service import ModuleService
from learning_platform.services.assessment_service import AssessmentService
from learning_platform.services.adaptive_learning_service import AdaptiveLearningService

__all__ = [
    "UserService",
    "ModuleService",
    "AssessmentService",
    "AdaptiveLearningService",
]
