"""
Basic tests for TB Coin Engine ML
Run with: python -m pytest tests/
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def test_health_check(self):
        """Test health endpoint"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "operational"
        assert "message" in data


class TestCoinOperations:
    """Test coin management operations"""
    
    def test_get_balance(self):
        """Test getting user balance"""
        response = client.get("/api/v1/coins/balance/testuser")
        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "balance" in data
    
    def test_mint_coins(self):
        """Test minting coins"""
        response = client.post("/api/v1/coins/mint/testuser?amount=100")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "balance" in data


class TestMLEndpoints:
    """Test ML/LLM functionality"""
    
    def test_analyze_transaction(self):
        """Test transaction analysis"""
        response = client.post(
            "/api/v1/ml/analyze-transaction"
            "?from_user=user1&to_user=user2&amount=100"
        )
        assert response.status_code == 200
        data = response.json()
        assert "analysis" in data
        assert "confidence" in data
    
    def test_predict_trend(self):
        """Test market trend prediction"""
        response = client.post("/api/v1/ml/predict-trend")
        assert response.status_code == 200
        data = response.json()
        assert "predictions" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
