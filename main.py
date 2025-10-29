"""
TB Coin Engine ML - Backend Application
Main application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import coins, transactions, ml_actions, health

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="ML-powered backend engine for TB Coin serverless operations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(coins.router, prefix="/api/v1", tags=["Coins"])
app.include_router(transactions.router, prefix="/api/v1", tags=["Transactions"])
app.include_router(ml_actions.router, prefix="/api/v1", tags=["ML Actions"])


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print(f"🚀 Starting {settings.APP_NAME}")
    print(f"📊 Environment: {settings.APP_ENV}")
    print(f"🤖 LLM Model: {settings.LLM_MODEL}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("👋 Shutting down TB Coin Engine")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "TB Coin Engine ML API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
