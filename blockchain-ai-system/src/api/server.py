"""FastAPI server exposing market data and AI predictions."""

from __future__ import annotations

from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.ai.models.price_predictor import PricePredictor
from src.data.collectors.coingecko_client import CoinGeckoClient
from src.data.collectors.deepseek_client import DeepSeekClient
from src.api.simple_index import router as simple_router
from src.monitoring.grafana_client import GrafanaClient, probe_optional_libs

app = FastAPI(title="AI Blockchain API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Expose a minimal Simple Repository API at /simple/
app.include_router(simple_router)

coingecko = CoinGeckoClient()
deepseek = DeepSeekClient()
predictor = PricePredictor()


@app.get("/")
async def root() -> Dict[str, str]:
    return {"message": "AI Blockchain API", "status": "running"}


@app.get("/health")
async def health(verbose: bool = False) -> Dict[str, Any]:
    """Basic health, with optional verbose probes.

    - Always returns status: healthy if app is up.
    - When verbose=true, includes optional libs availability and grafana status.
    """
    payload: Dict[str, Any] = {"status": "healthy"}
    if verbose:
        payload["optional_libs"] = probe_optional_libs()
        grafana = GrafanaClient()
        payload["grafana"] = grafana.availability() | {"health": grafana.health()}
    return payload


@app.get("/api/market/data")
async def get_market_data(limit: int = 20) -> Dict[str, Any]:
    data = await coingecko.get_top_cryptos(limit)
    return {"data": data, "count": len(data)}


async def _ensure_model_trained(market_data: list[dict[str, Any]]) -> None:
    if not predictor.is_trained:
        predictor.train(market_data)


@app.get("/api/ai/predict/{coin_id}")
async def predict_coin(coin_id: str) -> Dict[str, Any]:
    try:
        market_data = await coingecko.get_top_cryptos(50)
        coin_data = next((coin for coin in market_data if coin.get("id") == coin_id), None)
        if not coin_data:
            raise HTTPException(status_code=404, detail="Coin not found")

        # Train and prepare snapshot only if ML stack is available
        if getattr(predictor, "available", False):
            await _ensure_model_trained(market_data)
            features_frame: Any = predictor.prepare_features(market_data)
            try:
                if hasattr(features_frame, "loc") and hasattr(features_frame, "__getitem__"):
                    # Treat as a pandas DataFrame-like object
                    coin_features = features_frame.loc[features_frame["id"] == coin_id]
                    if not coin_features.empty:  # type: ignore[attr-defined]
                        current_snapshot = coin_features.iloc[-1].to_dict()  # type: ignore[attr-defined]
                    else:
                        current_snapshot = coin_data
                else:
                    # Fallback: treat as list[dict]
                    matching = [
                        row for row in features_frame
                        if isinstance(row, dict) and row.get("id") == coin_id
                    ]
                    current_snapshot = matching[-1] if matching else coin_data
            except Exception:
                current_snapshot = coin_data
        else:
            current_snapshot = coin_data

        ai_analysis = await deepseek.analyze_market(coin_data)
        ml_prediction = predictor.predict(current_snapshot)

        return {
            "coin": coin_data.get("name"),
            "ai_analysis": ai_analysis,
            "ml_prediction": ml_prediction,
        }
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - safeguard service
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/gas/optimization")
async def get_gas_optimization() -> Dict[str, Any]:
    network_data = {
        "base_fee": 15,
        "pending_transactions": 12_500,
        "average_gas_used": 21_000,
        "network_utilization": 0.65,
    }
    optimization = await deepseek.optimize_gas(network_data)
    return {"network_data": network_data, "optimization": optimization}


if __name__ == "__main__":  # pragma: no cover - manual execution helper
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

# Metrics and Grafana endpoints
@app.get("/api/metrics/grafana/availability")
async def grafana_availability() -> Dict[str, Any]:
    g = GrafanaClient()
    return g.availability()


@app.get("/api/metrics/grafana/health")
async def grafana_health() -> Dict[str, Any]:
    g = GrafanaClient()
    return g.health()


@app.get("/api/metrics/grafana/dashboard/{uid}")
async def grafana_dashboard(uid: str) -> Dict[str, Any]:
    g = GrafanaClient()
    return g.get_dashboard(uid)
