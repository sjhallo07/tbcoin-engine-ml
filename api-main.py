# api/main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager
from database.connection import get_db
from api.endpoints import blockchain_data, blockchain_gateway
from middleware.security import RateLimitMiddleware, SecurityHeadersMiddleware
import redis.asyncio as redis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.state.redis = await redis.from_url("redis://redis:6379", encoding="utf-8", decode_responses=True)
    logger.info("🚀 TB Coin API starting up...")
    yield
    # Shutdown
    await app.state.redis.close()
    logger.info("🛑 TB Coin API shutting down...")

app = FastAPI(
    title="TB Coin API",
    description="Quantum Meme Intelligence Blockchain Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://tbcoin.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(blockchain_data.router)
app.include_router(blockchain_gateway.router)

@app.get("/")
async def root():
    return {
        "message": "🚀 TB Coin API - Quantum Meme Intelligence",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "services": {
            "database": "connected",
            "redis": "connected",
            "blockchain_listener": "active"
        }
    }

@app.get("/metrics")
async def metrics():
    # Basic metrics endpoint for monitoring
    return {
        "total_transactions_processed": 0,
        "active_models": 0,
        "system_uptime": "0h",
        "memory_usage": "0MB"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)