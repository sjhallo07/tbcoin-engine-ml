from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict
import os

from solana_adapter import SolanaAdapter
from ai_decision_engine import AIDecisionEngine
from kms_signer import get_signer_from_env, is_simulation_mode

router = APIRouter(prefix="/api/v1/solana", tags=["solana"])

adapter = SolanaAdapter()
engine = AIDecisionEngine()
engine.load_model()
signer = get_signer_from_env()


class DecisionPayload(BaseModel):
    features: Dict[str, Any] = {}


@router.get("/balance/{pubkey}")
async def balance(pubkey: str):
    result = adapter.get_balance(pubkey)
    if isinstance(result, dict) and result.get("error"):
        raise HTTPException(status_code=503, detail=result["error"])
    return result


@router.get("/account/{pubkey}")
async def account(pubkey: str):
    result = adapter.get_account_info(pubkey)
    if isinstance(result, dict) and result.get("error"):
        raise HTTPException(status_code=503, detail=result["error"])
    return result


@router.post("/decision")
async def decision(payload: DecisionPayload):
    decision = engine.predict(payload.features)
    return {"decision": decision}


@router.post("/execute_decision")
async def execute_decision(payload: DecisionPayload):
    decision = engine.predict(payload.features)
    trading_enabled = os.getenv("AI_TRADING_ENABLED", "false").lower() in ("1", "true", "yes")

    if is_simulation_mode() or not trading_enabled:
        return {"decision": decision, "executed": False, "reason": "simulation_or_trading_disabled"}

    # In non-simulated mode attempt to prepare a transaction and send it.
    # This is a placeholder: real implementation must prepare a solana Transaction
    try:
        tx = None
        resp = adapter.send_transaction(tx, signer)
        return {"decision": decision, "executed": True, "response": resp}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
