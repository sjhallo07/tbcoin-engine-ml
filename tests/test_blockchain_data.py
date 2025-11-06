"""
Tests for blockchain data access endpoints
Run with: python -m pytest tests/test_blockchain_data.py -v
"""
import pytest
from fastapi.testclient import TestClient


# Use api.main for the application
try:
    from api.main import app
except ImportError:
    # Fallback to main.py if api.main doesn't work
    from main import app


client = TestClient(app)


class TestBlockchainDataEndpoints:
    """Test blockchain data access endpoints"""
    
    def test_get_transactions_no_filters(self):
        """Test getting transactions without filters"""
        response = client.get("/api/v1/blockchain/transactions")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert "count" in data
        assert isinstance(data["data"], list)
    
    def test_get_transactions_with_wallet_filter(self):
        """Test getting transactions filtered by wallet address"""
        response = client.get(
            "/api/v1/blockchain/transactions?wallet_address=0x123abc"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
    
    def test_get_transactions_with_time_range(self):
        """Test getting transactions with time range filter"""
        response = client.get(
            "/api/v1/blockchain/transactions?start_time=1000&end_time=2000"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
    
    def test_get_transactions_with_pagination(self):
        """Test getting transactions with pagination"""
        response = client.get(
            "/api/v1/blockchain/transactions?limit=10&offset=5"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["count"] <= 10
    
    def test_get_transactions_limit_validation(self):
        """Test that limit validation works (max 10000)"""
        response = client.get(
            "/api/v1/blockchain/transactions?limit=15000"
        )
        # Should return validation error
        assert response.status_code == 422


class TestWalletBehaviorEndpoints:
    """Test wallet behavior analysis endpoints"""
    
    def test_get_wallet_behavior(self):
        """Test getting wallet behavior analysis"""
        wallet_address = "0xtest123"
        response = client.get(
            f"/api/v1/blockchain/wallet/{wallet_address}/behavior"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["wallet_address"] == wallet_address
        assert "behavior_metrics" in data
    
    def test_get_wallet_behavior_with_different_address(self):
        """Test getting behavior for different wallet address"""
        wallet_address = "0xabc456"
        response = client.get(
            f"/api/v1/blockchain/wallet/{wallet_address}/behavior"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["wallet_address"] == wallet_address


class TestMLPredictionEndpoints:
    """Test ML prediction endpoints"""
    
    def test_make_prediction_default_model(self):
        """Test making prediction with default model"""
        request_data = {
            "features": {
                "price": 100.0,
                "volume": 1000,
                "trend": "up"
            }
        }
        response = client.post(
            "/api/v1/blockchain/predict",
            json=request_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "prediction" in data
        assert data["model_used"] == "price_movement"
    
    def test_make_prediction_risk_model(self):
        """Test making prediction with risk assessment model"""
        request_data = {
            "features": {
                "transaction_amount": 5000,
                "user_history": "good"
            },
            "model_type": "risk_assessment"
        }
        response = client.post(
            "/api/v1/blockchain/predict",
            json=request_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["model_used"] == "risk_assessment"
    
    def test_make_prediction_anomaly_model(self):
        """Test making prediction with anomaly detection model"""
        request_data = {
            "features": {
                "amount": 1000,
                "frequency": "high"
            },
            "model_type": "transaction_anomaly"
        }
        response = client.post(
            "/api/v1/blockchain/predict",
            json=request_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["model_used"] == "transaction_anomaly"
    
    def test_get_model_metrics(self):
        """Test getting model metrics"""
        response = client.get("/api/v1/blockchain/model/metrics")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "metrics" in data
        assert "models" in data["metrics"]
        assert "system_metrics" in data["metrics"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
