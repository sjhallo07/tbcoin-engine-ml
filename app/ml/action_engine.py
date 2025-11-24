"""ML Action Engine for processing intelligent actions"""
from typing import Dict, Optional
from datetime import datetime
import uuid
from app.models.schemas import MLActionRequest, MLActionResponse
from app.ml.llm_service import llm_service


class MLActionEngine:
    """
    ML-powered action engine for TB Coin operations
    Coordinates between different ML services and business logic
    """
    
    def __init__(self):
        self.llm_service = llm_service
    
    async def process_action(
        self, 
        action_request: MLActionRequest,
        user_balance: Optional[float] = None
    ) -> MLActionResponse:
        """
        Process an ML action request
        
        Args:
            action_request: The action request to process
            user_balance: Optional user balance information
            
        Returns:
            MLActionResponse with results
        """
        action_type = action_request.action_type.lower()
        
        # Route to appropriate handler
        if action_type == "analyze":
            result = await self._handle_analyze(action_request, user_balance)
        elif action_type == "recommend":
            result = await self._handle_recommend(action_request, user_balance)
        elif action_type == "predict":
            result = await self._handle_predict(action_request)
        elif action_type == "optimize":
            result = await self._handle_optimize(action_request)
        elif action_type == "transfer":
            result = await self._handle_transfer(action_request, user_balance)
        else:
            result = {
                "error": f"Unknown action type: {action_request.action_type}",
                "success": False
            }
        
        # Create response
        return MLActionResponse(
            action_type=action_request.action_type,
            result=result.get("result", result),
            confidence=result.get("confidence", 0.0),
            reasoning=result.get("reasoning"),
            recommendations=result.get("recommendations", []),
            timestamp=datetime.utcnow()
        )
    
    async def _handle_analyze(
        self, 
        request: MLActionRequest, 
        user_balance: Optional[float]
    ) -> Dict:
        """Handle analysis actions"""
        context = request.parameters
        
        if request.use_llm:
            analysis = await self.llm_service.analyze_transaction({
                "from_user": request.user_id,
                "to_user": context.get("to_user", "unknown"),
                "amount": context.get("amount", 0)
            })
            
            return {
                "result": analysis,
                "confidence": 1 - analysis.get("fraud_score", 0),
                "reasoning": f"LLM analysis: {analysis.get('risk_level', 'unknown')} risk",
                "recommendations": analysis.get("recommendations", [])
            }
        
        # Fallback analysis
        return {
            "result": {
                "risk_level": "low",
                "analysis": "Basic rule-based analysis"
            },
            "confidence": 0.6,
            "reasoning": "Rule-based analysis without LLM"
        }
    
    async def _handle_recommend(
        self, 
        request: MLActionRequest, 
        user_balance: Optional[float]
    ) -> Dict:
        """Handle recommendation actions"""
        if request.use_llm:
            user_context = {
                "user_id": request.user_id,
                "balance": user_balance or 0,
                "staked_balance": request.parameters.get("staked_balance", 0),
                "context": request.parameters.get("context", "")
            }
            
            recommendations = await self.llm_service.recommend_actions(user_context)
            
            return {
                "result": recommendations,
                "confidence": recommendations.get("confidence", 0.7),
                "reasoning": recommendations.get("reasoning", ""),
                "recommendations": recommendations.get("recommendations", [])
            }
        
        # Basic recommendations
        recs = []
        if user_balance and user_balance > 1000:
            recs.append("Consider staking part of your balance")
        if user_balance and user_balance < 100:
            recs.append("Accumulate more coins for better opportunities")
        
        return {
            "result": {"recommendations": recs},
            "confidence": 0.6,
            "recommendations": recs
        }
    
    async def _handle_predict(self, request: MLActionRequest) -> Dict:
        """Handle prediction actions"""
        historical_data = request.parameters.get("historical_data", [])
        
        if request.use_llm:
            predictions = await self.llm_service.predict_market_trend(historical_data)
            
            return {
                "result": predictions,
                "confidence": predictions.get("confidence", 0.5),
                "reasoning": "LLM-based market trend analysis",
                "recommendations": [
                    f"Short-term: {predictions.get('short_term', 'unknown')}",
                    f"Medium-term: {predictions.get('medium_term', 'unknown')}"
                ]
            }
        
        return {
            "result": {
                "trend": "stable",
                "prediction": "Basic trend analysis"
            },
            "confidence": 0.5
        }
    
    async def _handle_optimize(self, request: MLActionRequest) -> Dict:
        """Handle optimization actions"""
        transaction_params = request.parameters
        
        if request.use_llm:
            optimization = await self.llm_service.optimize_transaction(transaction_params)
            
            return {
                "result": optimization,
                "confidence": 0.8,
                "reasoning": optimization.get("reasoning", ""),
                "recommendations": [
                    f"Optimal timing: {optimization.get('optimal_timing', 'immediate')}",
                    f"Suggested fee: {optimization.get('suggested_fee', 'standard')}"
                ]
            }
        
        return {
            "result": {
                "optimization": "Standard parameters recommended"
            },
            "confidence": 0.6
        }
    
    async def _handle_transfer(
        self, 
        request: MLActionRequest, 
        user_balance: Optional[float]
    ) -> Dict:
        """Handle intelligent transfer actions"""
        amount = request.parameters.get("amount", 0)
        to_user = request.parameters.get("to_user", "")
        
        # Validate balance
        if user_balance is not None and amount > user_balance:
            return {
                "result": {
                    "success": False,
                    "error": "Insufficient balance"
                },
                "confidence": 1.0,
                "reasoning": "Balance check failed"
            }
        
        # Analyze transaction if LLM enabled
        if request.use_llm:
            analysis = await self.llm_service.analyze_transaction({
                "from_user": request.user_id,
                "to_user": to_user,
                "amount": amount
            })
            
            # Check risk level
            if analysis.get("fraud_score", 0) > 0.8:
                return {
                    "result": {
                        "success": False,
                        "warning": "High fraud risk detected",
                        "analysis": analysis
                    },
                    "confidence": 1 - analysis.get("fraud_score", 0),
                    "reasoning": "Transaction blocked due to high risk",
                    "recommendations": ["Verify recipient", "Use smaller amounts", "Contact support"]
                }
        
        return {
            "result": {
                "success": True,
                "ready_for_execution": True,
                "amount": amount,
                "to_user": to_user
            },
            "confidence": 0.9,
            "reasoning": "Transaction validated and ready",
            "recommendations": ["Proceed with transaction"]
        }


# Singleton instance
ml_engine = MLActionEngine()
