"""
TB Coin Engine ML - Backend Application
Main application entry point

This module provides the main FastAPI application with:
- Modular route organization
- Security middleware (rate limiting, input sanitization)
- Authentication with JWT
- Comprehensive error handling
- Structured logging
- Database connection management
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import coins, transactions, ml_actions, health
from app.middleware.logging import LoggingMiddleware
from app.middleware.security import SecurityHeadersMiddleware, InputSanitizationMiddleware
from app.middleware.error_handler import error_handler
from app.db.connection_manager import get_db_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("tbcoin")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events
    
    Handles startup and shutdown of the application,
    including database connection management.
    """
    # Startup
    logger.info(f"🚀 Starting {settings.APP_NAME}")
    logger.info(f"📊 Environment: {settings.APP_ENV}")
    logger.info(f"🤖 LLM Model: {settings.LLM_MODEL}")
    
    # Initialize database connections
    try:
        db_manager = await get_db_manager()
        logger.info("Database connections initialized")
    except Exception as e:
        logger.warning(f"Database initialization warning: {e}")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down TB Coin Engine")
    try:
        db_manager = await get_db_manager()
        await db_manager.shutdown()
        logger.info("Database connections closed")
    except Exception as e:
        logger.warning(f"Database shutdown warning: {e}")


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="ML-powered backend engine for TB Coin serverless operations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Register error handlers
error_handler(app)

# Add security middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(InputSanitizationMiddleware, strict_mode=False)
app.add_middleware(LoggingMiddleware)

# Configure CORS with appropriate origins
cors_origins = ["http://localhost:3000", "http://localhost:3001"]
if settings.APP_ENV == "production":
    cors_origins = ["https://tbcoin.com", "https://app.tbcoin.com"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(coins.router, prefix="/api/v1", tags=["Coins"])
app.include_router(transactions.router, prefix="/api/v1", tags=["Transactions"])
app.include_router(ml_actions.router, prefix="/api/v1", tags=["ML Actions"])


@app.get("/")
async def root():
    """Root endpoint
    
    Returns API information and status.
    """
    return {
        "message": "TB Coin Engine ML API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "endpoints": {
            "health": "/api/v1/health",
            "coins": "/api/v1/coins",
            "transactions": "/api/v1/transactions",
            "ml": "/api/v1/ml",
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
