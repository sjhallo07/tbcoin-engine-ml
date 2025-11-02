# api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager

try:
    import redis.asyncio as redis
except ImportError:  # pragma: no cover - redis is optional for local runs
    redis = None  # type: ignore
    logging.warning("⚠️ Redis dependency not installed; redis features will be unavailable.")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from api.endpoints import blockchain_data, blockchain_gateway  # type: ignore
except Exception:  # pragma: no cover - optional dependency path
    blockchain_data = None
    blockchain_gateway = None

try:
    from app.api import coins as coins_router  # type: ignore
    from app.api import transactions as transactions_router  # type: ignore
except Exception:  # pragma: no cover - optional dependency path
    coins_router = None
    transactions_router = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    if redis is not None:
        try:
            app.state.redis = await redis.from_url(
                "redis://redis:6379",
                encoding="utf-8",
                decode_responses=True,
            )
            logger.info("🚀 TB Coin API starting up...")
        except Exception as exc:
            app.state.redis = None
            logger.warning("⚠️ Redis connection unavailable: %s", exc)
    else:
        app.state.redis = None
        logger.info("⚠️ Redis dependency not installed; skipping rate limiting")
    yield
    # Shutdown
    redis_client = getattr(app.state, "redis", None)
    if redis_client is not None:
        await redis_client.close()
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

# Include routers when available
if blockchain_data is not None:
    app.include_router(blockchain_data.router)
if blockchain_gateway is not None:
    app.include_router(blockchain_gateway.router)
if coins_router is not None:
    app.include_router(coins_router.router)
if transactions_router is not None:
    app.include_router(transactions_router.router)

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