"""Health check endpoints"""
from fastapi import APIRouter
from datetime import datetime
from app.models.schemas import HealthStatus
from app.core.config import settings

router = APIRouter()


@router.get("/health", response_model=HealthStatus)
async def health_check():
    """Health check endpoint"""
    return HealthStatus(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.utcnow(),
        services={
            "api": "operational",
            "ml_engine": "operational",
            "llm_service": "operational" if settings.OPENAI_API_KEY else "fallback_mode"
        }
    )


@router.get("/health/live")
async def liveness():
    """Kubernetes liveness probe"""
    return {"status": "alive"}


@router.get("/health/ready")
async def readiness():
    """Kubernetes readiness probe"""
    return {"status": "ready"}
