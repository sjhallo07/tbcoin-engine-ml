"""ML-powered action endpoints"""
from fastapi import APIRouter, HTTPException
from app.models.schemas import MLActionRequest, MLActionResponse
from app.ml.action_engine import ml_engine
from app.services.coin_service import coin_service

router = APIRouter()


@router.post("/ml/action", response_model=MLActionResponse)
async def process_ml_action(request: MLActionRequest):
    """
    Process an ML-powered action
    
    Args:
        request: ML action request
        
    Returns:
        ML action response with results and recommendations
    """
    try:
        # Get user balance for context
        balance_obj = await coin_service.get_balance(request.user_id)
        user_balance = balance_obj.balance
        
        # Process action through ML engine
        response = await ml_engine.process_action(request, user_balance)
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ml/analyze-transaction")
async def analyze_transaction(
    from_user: str,
    to_user: str,
    amount: float
):
    """
    Analyze a transaction using ML/LLM
    
    Args:
        from_user: Sender user ID
        to_user: Receiver user ID
        amount: Transaction amount
        
    Returns:
        Analysis results with risk assessment
    """
    try:
        request = MLActionRequest(
            action_type="analyze",
            user_id=from_user,
            parameters={
                "to_user": to_user,
                "amount": amount
            },
            use_llm=True
        )
        
        response = await ml_engine.process_action(request)
        
        return {
            "analysis": response.result,
            "confidence": response.confidence,
            "reasoning": response.reasoning,
            "recommendations": response.recommendations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ml/recommend")
async def get_recommendations(
    user_id: str,
    context: str = ""
):
    """
    Get personalized recommendations for a user
    
    Args:
        user_id: User identifier
        context: Additional context for recommendations
        
    Returns:
        Personalized recommendations
    """
    try:
        # Get user balance
        balance_obj = await coin_service.get_balance(user_id)
        
        request = MLActionRequest(
            action_type="recommend",
            user_id=user_id,
            parameters={
                "context": context,
                "staked_balance": balance_obj.staked_balance
            },
            use_llm=True
        )
        
        response = await ml_engine.process_action(request, balance_obj.balance)
        
        return {
            "recommendations": response.recommendations,
            "reasoning": response.reasoning,
            "confidence": response.confidence,
            "user_balance": balance_obj.balance,
            "staked_balance": balance_obj.staked_balance
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ml/predict-trend")
async def predict_market_trend():
    """
    Predict market trends using ML
    
    Returns:
        Market trend predictions
    """
    try:
        request = MLActionRequest(
            action_type="predict",
            user_id="system",
            parameters={
                "historical_data": []  # In production, fetch real data
            },
            use_llm=True
        )
        
        response = await ml_engine.process_action(request)
        
        return {
            "predictions": response.result,
            "confidence": response.confidence,
            "reasoning": response.reasoning
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ml/optimize-transaction")
async def optimize_transaction(
    user_id: str,
    amount: float,
    transaction_type: str = "send"
):
    """
    Optimize transaction parameters using ML
    
    Args:
        user_id: User identifier
        amount: Transaction amount
        transaction_type: Type of transaction
        
    Returns:
        Optimized transaction parameters
    """
    try:
        request = MLActionRequest(
            action_type="optimize",
            user_id=user_id,
            parameters={
                "amount": amount,
                "type": transaction_type,
                "fee": amount * 0.005  # Current fee
            },
            use_llm=True
        )
        
        response = await ml_engine.process_action(request)
        
        return {
            "optimization": response.result,
            "confidence": response.confidence,
            "reasoning": response.reasoning,
            "recommendations": response.recommendations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ml/intelligent-transfer")
async def intelligent_transfer(
    from_user: str,
    to_user: str,
    amount: float,
    auto_execute: bool = False
):
    """
    Perform intelligent transfer with ML analysis
    
    Args:
        from_user: Sender user ID
        to_user: Receiver user ID
        amount: Amount to transfer
        auto_execute: Whether to auto-execute if approved
        
    Returns:
        Transfer analysis and optionally executed transaction
    """
    try:
        # Get user balance
        balance_obj = await coin_service.get_balance(from_user)
        
        request = MLActionRequest(
            action_type="transfer",
            user_id=from_user,
            parameters={
                "to_user": to_user,
                "amount": amount
            },
            use_llm=True
        )
        
        response = await ml_engine.process_action(request, balance_obj.balance)
        
        result = {
            "analysis": response.result,
            "confidence": response.confidence,
            "reasoning": response.reasoning,
            "recommendations": response.recommendations
        }
        
        # Auto-execute if approved and requested
        if auto_execute and response.result.get("success") and response.result.get("ready_for_execution"):
            from app.services.transaction_service import transaction_service
            from app.models.schemas import TransactionRequest
            
            txn_request = TransactionRequest(
                from_user=from_user,
                to_user=to_user,
                amount=amount
            )
            transaction = await transaction_service.create_transaction(txn_request)
            transaction = await transaction_service.execute_transaction(transaction.transaction_id)
            
            result["transaction"] = transaction
            result["executed"] = True
        else:
            result["executed"] = False
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
