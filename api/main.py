from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import os
import requests
from fastapi import HTTPException

# Basic logger for startup/liveness messages
logger = logging.getLogger("tbcoin")
logger.setLevel(logging.INFO)

# Configure a module-level logger for startup/health messages
logger = logging.getLogger("tbcoin")
if not logger.handlers:
    # Basic configuration for local development; containerized runs should
    # configure structured logging/handlers as appropriate.
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

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
# NEW - Import solana endpoints router
try:
    from api.solana_endpoints import router as solana_router
except Exception:
    solana_router = None

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
# NEW - Include solana endpoints when available
if solana_router is not None:
    app.include_router(solana_router)

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

@app.get("/health")
async def health():
    """Lightweight liveness endpoint for readiness probes and quick checks."""
    # Prefer the agent instance managed by the API routes module
    try:
        from api.autonomous_routes import autonomous_agent
    except Exception:
        autonomous_agent = None

    # Emit a small info log so container orchestrators and local runs show startup progress
    logger.info("/health requested - agent_enabled=%s, agent_running=%s",
                getattr(config, "AI_AGENT_ENABLED", False),
                bool(autonomous_agent and getattr(autonomous_agent, "is_running", False)))

    return {
        "status": "ok",
        "autonomous_agent_enabled": getattr(config, "AI_AGENT_ENABLED", False),
        "autonomous_agent_running": bool(autonomous_agent and getattr(autonomous_agent, "is_running", False))
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


@app.get("/messages")
async def messages():
    """Simple test endpoint returning sample messages for integration tests.

    Returns a small JSON payload so external HTTP tests (or local TestClient)
    can verify reachability and JSON parsing.
    """
    sample = {
        "messages": [
            {"id": 1, "text": "Hello from TB Coin API"},
            {"id": 2, "text": "This is a test message"}
        ]
    }
    # Also log a small startup/info line for visibility in container logs
    logger.info("/messages requested - returning %d messages", len(sample["messages"]))
    return sample


@app.get("/relay")
def relay(message: str | None = None, target: str | None = None):
    """Receive a message via GET and forward it as a POST to a target URL.

    Query parameters:
      - message: the message text to forward
      - target: optional override target POST URL (default from TEST_POST_URL env)

    Safety: honors SIMULATE_HTTP_POST env var (true/false). When simulation is
    enabled (default true) the endpoint will not perform the external POST and
    will instead return the payload and target for inspection.
    """
    target_url = target or os.getenv("TEST_POST_URL", "http://127.0.0.1:3000/messages")
    payload = {"message": message}

    simulate = os.getenv("SIMULATE_HTTP_POST", "true").lower() in ("1", "true", "yes")
    logger.info("/relay requested - simulate=%s target=%s", simulate, target_url)

    if simulate:
        return {"simulated": True, "target": target_url, "payload": payload}

    # Perform real POST
    try:
        resp = requests.post(target_url, json=payload, timeout=10)
    except Exception as exc:
        logger.error("/relay post to %s failed: %s", target_url, exc)
        raise HTTPException(status_code=502, detail=str(exc))

    # Attempt to parse JSON response when appropriate
    content_type = resp.headers.get("Content-Type", "")
    body: object
    try:
        if "application/json" in content_type:
            body = resp.json()
        else:
            body = resp.text
    except Exception:
        body = resp.text

    return {"simulated": False, "status_code": resp.status_code, "response": body}

