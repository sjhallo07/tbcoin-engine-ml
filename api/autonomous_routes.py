from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Optional
import asyncio
import inspect

from config import config
from agents.autonomous_agent import AutonomousTradingAgent
from agents.learning_feedback_loop import LearningFeedbackLoop

router = APIRouter(prefix="/api/v1/autonomous", tags=["autonomous-agent"])

# Instancia global del agente
autonomous_agent = None

class AgentControlRequest(BaseModel):
    action: str  # start, stop, status, analyze
    parameters: Optional[Dict] = None

class TradingDecisionRequest(BaseModel):
    market_data: Dict
    strategy: Optional[str] = "composite"
@router.on_event("startup")
async def startup_autonomous_agent():
    """Inicializar agente autónomo al iniciar la API"""
    global autonomous_agent
    if getattr(config, "AI_AGENT_ENABLED", False):
        autonomous_agent = AutonomousTradingAgent()
        # Iniciar en modo análisis (no trading automático) si el método existe
        start_analysis = getattr(autonomous_agent, "start_analysis_mode", None)
        if callable(start_analysis):
            # Si es una coroutine function, crear tarea directamente; si es síncrona, ejecutarla en un thread
            if inspect.iscoroutinefunction(start_analysis):
                asyncio.create_task(start_analysis())
            else:
                asyncio.create_task(asyncio.to_thread(start_analysis))
        else:
            # Intentar un nombre alternativo común si existe
            start_analysis_alt = getattr(autonomous_agent, "start_analysis", None)
            if callable(start_analysis_alt):
                if inspect.iscoroutinefunction(start_analysis_alt):
                    asyncio.create_task(start_analysis_alt())
                else:
                    asyncio.create_task(asyncio.to_thread(start_analysis_alt))

@router.post("/control")
async def control_autonomous_agent(request: AgentControlRequest):
    """Controlar el agente autónomo"""
    global autonomous_agent
    
    if request.action == "start":
        if autonomous_agent and not getattr(autonomous_agent, "is_running", False):
            asyncio.create_task(autonomous_agent.start_autonomous_trading())
            return {"status": "started", "message": "Autonomous trading started"}
    
    elif request.action == "stop":
        if autonomous_agent:
            autonomous_agent.is_running = False
            return {"status": "stopped", "message": "Autonomous trading stopped"}
    
    elif request.action == "status":
        status = {
            "is_running": autonomous_agent.is_running if autonomous_agent else False,
            "ai_enabled": getattr(config, "AI_AGENT_ENABLED", False),
            "trading_enabled": getattr(config, "AI_TRADING_ENABLED", False),
            "performance_metrics": getattr(autonomous_agent, "performance_metrics", {}) if autonomous_agent else {}
        }
        return status
    
    elif request.action == "analyze":
        if autonomous_agent:
            analysis = await autonomous_agent.analyze_current_market()
            return analysis
    
    raise HTTPException(status_code=400, detail="Invalid action")

@router.post("/analyze-market")
async def analyze_market(request: TradingDecisionRequest):
    """Análisis de mercado usando IA (sin ejecutar trades)"""
    if not autonomous_agent:
        raise HTTPException(status_code=503, detail="Autonomous agent not available")
    
    analysis = await autonomous_agent.decision_engine.analyze_market_context(
        request.market_data
    )
    
    return {
        "analysis": analysis,
        "recommendation": analysis.get('llm_recommendation'),
        "confidence": analysis.get('confidence_level'),
        "risk_assessment": analysis.get('risk_assessment')
    }

@router.get("/performance")
async def get_agent_performance():
    """Obtener métricas de performance del agente"""
    if not autonomous_agent:
        return {"error": "Agent not available"}
    
    # Safely get performance metrics
    performance_metrics = getattr(autonomous_agent, "performance_metrics", {})

    # Safely retrieve learning insights if the method exists (supports sync or async)
    learning_insights = []
    learning_loop = getattr(autonomous_agent, "learning_loop", None)
    if learning_loop is not None:
        getter = getattr(learning_loop, "get_recent_insights", None)
        if callable(getter):
            result = getter()
            if asyncio.iscoroutine(result):
                learning_insights = await result
            else:
                learning_insights = result

    # Safely retrieve strategy performance (supports sync or async)
    strategy_performance = {}
    get_strategy = getattr(autonomous_agent, "get_strategy_performance", None)
    if callable(get_strategy):
        sp_result = get_strategy()
        if asyncio.iscoroutine(sp_result):
            strategy_performance = await sp_result
        else:
            strategy_performance = sp_result

    return {
        "performance_metrics": performance_metrics,
        "learning_insights": learning_insights,
        "strategy_performance": strategy_performance or {}
    }

@router.post("/train-model")
async def train_ai_model(background_tasks: BackgroundTasks, model_type: str = "all"):
    """Entrenar modelos de IA en background"""
    background_tasks.add_task(train_models_background, model_type)
    
    return {
        "status": "training_started",
        "model_type": model_type,
        "message": "Model training started in background"
    }

async def train_models_background(model_type: str):
    """Función background para entrenar modelos"""
    # Imports done here to keep startup fast and avoid optional deps at import time
    try:
        from agents.ai_decision_engine import AutonomousDecisionEngine
    except Exception:
        AutonomousDecisionEngine = None

    try:
        from agents.reinforcement_learning_agent import ReinforcementLearningAgent
    except Exception:
        ReinforcementLearningAgent = None
    
    if model_type in ["price-prediction", "all"] and AutonomousDecisionEngine:
        engine = AutonomousDecisionEngine()
        if hasattr(engine, "train_price_prediction_model"):
            await engine.train_price_prediction_model()
    
    if model_type in ["reinforcement-learning", "all"] and ReinforcementLearningAgent:
        rl_agent = ReinforcementLearningAgent()
        if hasattr(rl_agent, "train"):
            await rl_agent.train()
