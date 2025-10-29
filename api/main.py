from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Import config
from config import config

# Importar routers existentes
try:
    from api.endpoints import blockchain_data, blockchain_gateway
except Exception:
    # Fallback: try to import from app.api if present
    try:
        from app.api import coins as blockchain_data  # type: ignore
        from app.api import transactions as blockchain_gateway  # type: ignore
    except Exception:
        blockchain_data = None
        blockchain_gateway = None

# NEW - Importar autonomous agent routes
from api.autonomous_routes import router as autonomous_router

app = FastAPI(
    title="TB Coin API - Quantum Meme Intelligence",
    description="Plataforma completa de blockchain con IA autónoma",
    version="2.0.0"
)

# CORS (allow local frontend during development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include existing routers if available
if blockchain_data is not None:
    app.include_router(blockchain_data.router)
if blockchain_gateway is not None:
    app.include_router(blockchain_gateway.router)

# NEW - Include autonomous agent routes
app.include_router(autonomous_router)

@app.get("/")
async def root():
    return {
        "message": "🚀 TB Coin API - Quantum Meme Intelligence",
        "version": "2.0.0",
        "features": {
            "blockchain": "active",
            "smart_contracts": "active",
            "autonomous_ai": "active" if getattr(config, "AI_AGENT_ENABLED", False) else "inactive",
            "machine_learning": "active"
        }
    }

@app.get("/status")
async def status():
    """Endpoint de status extendido"""
    # Prefer the agent instance managed by the API routes module
    try:
        from api.autonomous_routes import autonomous_agent
    except Exception:
        autonomous_agent = None

    return {
        "api": "healthy",
        "database": "connected",
        "blockchain": "connected",
        "autonomous_agent": {
            "enabled": getattr(config, "AI_AGENT_ENABLED", False),
            "trading_enabled": getattr(config, "AI_TRADING_ENABLED", False),
            "status": "running" if autonomous_agent and getattr(autonomous_agent, "is_running", False) else "stopped"
        }
    }
