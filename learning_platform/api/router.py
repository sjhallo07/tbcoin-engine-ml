"""Main router combining all API endpoints."""
from fastapi import APIRouter

from learning_platform.api.endpoints import users, modules, assessments, progress

router = APIRouter(prefix="/learning", tags=["Learning Platform"])

# Include all endpoint routers
router.include_router(users.router, prefix="/users", tags=["Users"])
router.include_router(modules.router, prefix="/modules", tags=["Modules"])
router.include_router(assessments.router, prefix="/assessments", tags=["Assessments"])
router.include_router(progress.router, prefix="/progress", tags=["Progress"])


@router.get("/")
async def learning_platform_root():
    """Learning Platform API root endpoint."""
    return {
        "name": "AI Learning Platform",
        "version": "1.0.0",
        "description": "Python Machine Learning education platform",
        "endpoints": {
            "users": "/learning/users",
            "modules": "/learning/modules",
            "assessments": "/learning/assessments",
            "progress": "/learning/progress"
        }
    }


@router.get("/catalog")
async def get_catalog():
    """Get learning module catalog organized by difficulty."""
    return {
        "beginner": [
            {
                "slug": "scikit-learn-basics",
                "title": "Scikit-Learn Basics",
                "library": "scikit-learn",
                "description": "Introduction to machine learning with Scikit-Learn"
            },
            {
                "slug": "linear-regression",
                "title": "Linear Regression",
                "library": "scikit-learn",
                "description": "Understanding and implementing linear regression"
            },
            {
                "slug": "decision-trees",
                "title": "Decision Trees",
                "library": "scikit-learn",
                "description": "Classification with decision trees"
            }
        ],
        "intermediate": [
            {
                "slug": "tensorflow-intro",
                "title": "TensorFlow Introduction",
                "library": "tensorflow",
                "description": "Getting started with TensorFlow"
            },
            {
                "slug": "pytorch-fundamentals",
                "title": "PyTorch Fundamentals",
                "library": "pytorch",
                "description": "Deep learning with PyTorch"
            },
            {
                "slug": "overfitting-underfitting",
                "title": "Overfitting vs Underfitting",
                "library": "general",
                "description": "Understanding model complexity"
            }
        ],
        "advanced": [
            {
                "slug": "ensemble-learning",
                "title": "Ensemble Learning",
                "library": "xgboost",
                "description": "XGBoost and LightGBM techniques"
            },
            {
                "slug": "hyperparameter-tuning",
                "title": "Hyperparameter Tuning",
                "library": "scikit-learn",
                "description": "Advanced model optimization"
            },
            {
                "slug": "reinforcement-learning",
                "title": "Reinforcement Learning",
                "library": "stable-baselines3",
                "description": "RL algorithms and applications"
            }
        ]
    }
