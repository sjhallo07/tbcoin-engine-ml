# api/endpoints/blockchain_data.py
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import logging

router = APIRouter(prefix="/api/v1/blockchain", tags=["blockchain-data"])

class TransactionQuery(BaseModel):
    wallet_address: Optional[str] = None
    start_time: Optional[int] = None
    end_time: Optional[int] = None
    limit: int = 1000
    offset: int = 0

class ModelPredictionRequest(BaseModel):
    features: Dict[str, Any]
    model_type: str = "price_movement"

@router.get("/transactions")
async def get_transactions(
    wallet_address: Optional[str] = Query(None),
    start_time: Optional[int] = Query(None),
    end_time: Optional[int] = Query(None),
    limit: int = Query(1000, le=10000),
    offset: int = Query(0)
):
    """Get transaction data for analysis"""
    try:
        transactions = await blockchain_service.get_transactions(
            wallet_address=wallet_address,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
            offset=offset
        )
        return {
            "status": "success",
            "data": transactions,
            "count": len(transactions)
        }
    except Exception as e:
        logging.error(f"Error fetching transactions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/wallet/{wallet_address}/behavior")
async def get_wallet_behavior(wallet_address: str):
    """Get wallet behavior analysis"""
    try:
        behavior_data = await analytics_service.analyze_wallet_behavior(wallet_address)
        return {
            "status": "success",
            "wallet_address": wallet_address,
            "behavior_metrics": behavior_data
        }
    except Exception as e:
        logging.error(f"Error analyzing wallet behavior: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/predict")
async def make_prediction(request: ModelPredictionRequest):
    """Make prediction using trained ML models"""
    try:
        prediction = await ml_service.predict(
            features=request.features,
            model_type=request.model_type
        )
        return {
            "status": "success",
            "prediction": prediction,
            "model_used": request.model_type
        }
    except Exception as e:
        logging.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail="Prediction failed")

@router.get("/model/metrics")
async def get_model_metrics():
    """Get current model performance metrics"""
    try:
        metrics = await ml_service.get_model_metrics()
        return {
            "status": "success",
            "metrics": metrics
        }
    except Exception as e:
        logging.error(f"Error fetching model metrics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")