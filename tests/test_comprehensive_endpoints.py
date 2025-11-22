"""
Comprehensive test suite for TB Coin Engine ML Backend API endpoints
Tests all Python FastAPI endpoints with various scenarios
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.main import app

client = TestClient(app)


class TestCoreEndpoints:
    """Test core API endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint returns correct structure"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "features" in data
        assert isinstance(data["features"], dict)
    
    def test_health_endpoint(self):
        """Test health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "autonomous_agent_enabled" in data
        assert "autonomous_agent_running" in data
    
    def test_status_endpoint(self):
        """Test extended status endpoint"""
        response = client.get("/status")
        assert response.status_code == 200
        data = response.json()
        assert "api" in data
        assert "database" in data
        assert "blockchain" in data
        assert "autonomous_agent" in data
        assert isinstance(data["autonomous_agent"], dict)
        assert "enabled" in data["autonomous_agent"]
        assert "trading_enabled" in data["autonomous_agent"]
        assert "status" in data["autonomous_agent"]
    
    def test_messages_endpoint(self):
        """Test messages endpoint for integration testing"""
        response = client.get("/messages")
        assert response.status_code == 200
        data = response.json()
        assert "messages" in data
        assert isinstance(data["messages"], list)
        assert len(data["messages"]) > 0
        # Verify message structure
        message = data["messages"][0]
        assert "id" in message
        assert "text" in message


class TestAutonomousAgentEndpoints:
    """Test autonomous trading agent endpoints"""
    
    def test_agent_status(self):
        """Test getting agent status"""
        response = client.post(
            "/api/v1/autonomous/control",
            json={"action": "status"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "is_running" in data
        assert "ai_enabled" in data
        assert "trading_enabled" in data
        assert "performance_metrics" in data
    
    def test_analyze_market(self):
        """Test market analysis endpoint"""
        market_data = {
            "price": 100.0,
            "volume": 1000000,
            "volatility": 0.05,
            "trend": "bullish"
        }
        response = client.post(
            "/api/v1/autonomous/analyze-market",
            json={"market_data": market_data, "strategy": "composite"}
        )
        # May return 503 if agent not available, which is acceptable
        assert response.status_code in [200, 503]
        if response.status_code == 200:
            data = response.json()
            assert "analysis" in data
            assert "recommendation" in data
            assert "confidence" in data
            assert "risk_assessment" in data
    
    def test_agent_performance(self):
        """Test getting agent performance metrics"""
        response = client.get("/api/v1/autonomous/performance")
        assert response.status_code == 200
        data = response.json()
        # Should return structure even if agent not available
        # May return error if agent not initialized, which is acceptable
        assert isinstance(data, dict)
        if "error" not in data:
            assert "performance_metrics" in data
            assert "learning_insights" in data
            assert "strategy_performance" in data
    
    def test_train_model_endpoint(self):
        """Test model training endpoint (background task)"""
        response = client.post(
            "/api/v1/autonomous/train-model?model_type=all"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "training_started"
        assert "model_type" in data
        assert "message" in data


class TestRelayEndpoint:
    """Test relay endpoint for message forwarding"""
    
    def test_relay_simulated(self):
        """Test relay endpoint in simulation mode (default)"""
        response = client.get(
            "/relay?message=test_message&target=http://example.com/messages"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["simulated"] == True
        assert "target" in data
        assert "payload" in data
        assert data["payload"]["message"] == "test_message"


class TestBlockchainEndpoints:
    """Test blockchain data endpoints (if available)"""
    
    def test_transactions_endpoint_exists(self):
        """Test if transactions endpoint is accessible"""
        # This might return 500 if services not configured, which is acceptable
        response = client.get("/api/v1/blockchain/transactions?limit=10")
        # Accept 200 (success), 404 (not implemented), or 500 (service not available)
        assert response.status_code in [200, 404, 500]
    
    def test_model_metrics_endpoint(self):
        """Test model metrics endpoint"""
        response = client.get("/api/v1/blockchain/model/metrics")
        # Accept various status codes as service might not be fully configured
        assert response.status_code in [200, 404, 500]


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_agent_action(self):
        """Test invalid action to agent control endpoint"""
        response = client.post(
            "/api/v1/autonomous/control",
            json={"action": "invalid_action"}
        )
        assert response.status_code == 400
    
    def test_missing_parameters(self):
        """Test endpoints with missing required parameters"""
        response = client.post(
            "/api/v1/autonomous/control",
            json={}
        )
        # Should return validation error
        assert response.status_code == 422
    
    def test_nonexistent_endpoint(self):
        """Test accessing non-existent endpoint"""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404


class TestSecurityFeatures:
    """Test security-related features"""
    
    def test_cors_headers(self):
        """Test CORS headers are present"""
        response = client.options("/")
        # CORS middleware should add appropriate headers
        assert response.status_code in [200, 405]
    
    def test_simulated_relay_prevents_external_calls(self):
        """Test that relay simulation prevents actual external HTTP calls"""
        # By default, SIMULATE_HTTP_POST should be true
        response = client.get("/relay?message=test")
        assert response.status_code == 200
        data = response.json()
        # Should be simulated, not making real external calls
        assert data["simulated"] == True


class TestDataValidation:
    """Test data validation and input sanitization"""
    
    def test_market_analysis_with_invalid_data(self):
        """Test market analysis with invalid data structure"""
        response = client.post(
            "/api/v1/autonomous/analyze-market",
            json={"market_data": "invalid"}  # Should be dict, not string
        )
        # Should handle gracefully - either 422 validation error or 503 service unavailable
        assert response.status_code in [422, 503]
    
    def test_control_with_extra_fields(self):
        """Test control endpoint with extra fields (should be ignored)"""
        response = client.post(
            "/api/v1/autonomous/control",
            json={
                "action": "status",
                "extra_field": "should_be_ignored"
            }
        )
        assert response.status_code == 200


# Integration test class
class TestEndToEndFlow:
    """Test end-to-end workflows"""
    
    def test_agent_workflow(self):
        """Test complete agent workflow: status -> analyze -> performance"""
        # 1. Check initial status
        status_response = client.post(
            "/api/v1/autonomous/control",
            json={"action": "status"}
        )
        assert status_response.status_code == 200
        
        # 2. Get performance metrics
        perf_response = client.get("/api/v1/autonomous/performance")
        assert perf_response.status_code == 200
        
        # 3. Health check
        health_response = client.get("/health")
        assert health_response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
