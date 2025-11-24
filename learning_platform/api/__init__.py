"""API endpoints for the AI Learning Platform."""
from learning_platform.api.router import router
from learning_platform.api.dependencies import get_db, get_current_user

__all__ = [
    "router",
    "get_db",
    "get_current_user",
]
