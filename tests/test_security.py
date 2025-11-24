"""
Tests for security middleware and input sanitization
Run with: python -m pytest tests/test_security.py -v
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from app.middleware.security import (
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
    InputSanitizationMiddleware,
)
from app.middleware.auth import JWTAuth, APIKeyAuth


class TestJWTAuth:
    """Test JWT authentication"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.jwt_auth = JWTAuth(
            secret_key="test-secret-key",
            algorithm="HS256",
            access_token_expire_minutes=30
        )
    
    def test_create_access_token(self):
        """Test creating an access token"""
        token = self.jwt_auth.create_access_token(
            data={"sub": "user123", "role": "user"}
        )
        assert token is not None
        assert len(token) > 0
    
    def test_verify_valid_token(self):
        """Test verifying a valid token"""
        token = self.jwt_auth.create_access_token(
            data={"sub": "user123", "role": "user"}
        )
        token_data = self.jwt_auth.verify_token(token)
        assert token_data is not None
        assert token_data.sub == "user123"
    
    def test_verify_invalid_token(self):
        """Test verifying an invalid token"""
        token_data = self.jwt_auth.verify_token("invalid-token")
        assert token_data is None
    
    def test_password_hashing(self):
        """Test password hashing and verification"""
        password = "SecurePassword123"
        hashed = self.jwt_auth.get_password_hash(password)
        
        assert hashed != password
        assert self.jwt_auth.verify_password(password, hashed) is True
        assert self.jwt_auth.verify_password("wrong-password", hashed) is False


class TestAPIKeyAuth:
    """Test API key authentication"""
    
    def test_valid_api_key(self):
        """Test validating a valid API key"""
        auth = APIKeyAuth(valid_keys=["valid-key-123"])
        assert auth.verify_key("valid-key-123") is True
    
    def test_invalid_api_key(self):
        """Test validating an invalid API key"""
        auth = APIKeyAuth(valid_keys=["valid-key-123"])
        assert auth.verify_key("invalid-key") is False
    
    def test_add_key(self):
        """Test adding a new API key"""
        auth = APIKeyAuth(valid_keys=[])
        auth.add_key("new-key")
        assert auth.verify_key("new-key") is True
    
    def test_remove_key(self):
        """Test removing an API key"""
        auth = APIKeyAuth(valid_keys=["key-to-remove"])
        auth.remove_key("key-to-remove")
        assert auth.verify_key("key-to-remove") is False


class TestInputSanitization:
    """Test input sanitization middleware"""
    
    def test_sanitize_sql_injection(self):
        """Test detection of SQL injection patterns"""
        # Create middleware instance
        middleware = InputSanitizationMiddleware(app=MagicMock(), strict_mode=False)
        
        # Test SQL injection pattern detection
        sql_patterns = [
            "SELECT * FROM users",
            "DROP TABLE users",
            "1'; DELETE FROM users; --",
        ]
        
        for pattern in sql_patterns:
            # In non-strict mode, should log but not block
            # This tests the internal pattern detection
            for regex in middleware.sql_regex:
                if regex.search(pattern):
                    break  # Pattern was detected
            else:
                pytest.fail(f"SQL injection pattern not detected: {pattern}")
    
    def test_sanitize_xss_patterns(self):
        """Test detection of XSS patterns"""
        middleware = InputSanitizationMiddleware(app=MagicMock(), strict_mode=False)
        
        xss_patterns = [
            "<script>alert('xss')</script>",
            "javascript:void(0)",
            "<img onerror='alert(1)'>",
            "<iframe src='evil.com'>",
        ]
        
        for pattern in xss_patterns:
            for regex in middleware.xss_regex:
                if regex.search(pattern):
                    break
            else:
                pytest.fail(f"XSS pattern not detected: {pattern}")
    
    def test_sanitize_string(self):
        """Test string sanitization"""
        dangerous = "<script>alert(1)</script>test"
        sanitized = InputSanitizationMiddleware.sanitize_string(dangerous)
        assert "<script>" not in sanitized
        assert "test" in sanitized
    
    def test_sanitize_dict(self):
        """Test dictionary sanitization"""
        dangerous_dict = {
            "name": "<script>alert(1)</script>John",
            "nested": {
                "value": "normal",
                "evil": "<img onerror='alert(1)'>"
            }
        }
        sanitized = InputSanitizationMiddleware.sanitize_dict(dangerous_dict)
        assert "<script>" not in sanitized["name"]
        assert "John" in sanitized["name"]


class TestSecurityHeadersMiddleware:
    """Test security headers middleware"""
    
    def test_security_headers_added(self):
        """Test that security headers are added to responses"""
        # Create a simple FastAPI app with the middleware
        app = FastAPI()
        app.add_middleware(SecurityHeadersMiddleware)
        
        @app.get("/test")
        async def test_endpoint():
            return {"message": "test"}
        
        client = TestClient(app)
        response = client.get("/test")
        
        # Check for security headers
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        assert response.headers.get("X-Frame-Options") == "DENY"
        assert response.headers.get("X-XSS-Protection") == "1; mode=block"
        assert "Strict-Transport-Security" in response.headers


class TestRateLimitMiddleware:
    """Test rate limiting middleware"""
    
    def test_rate_limit_initialization(self):
        """Test rate limiter initialization"""
        app = MagicMock()
        middleware = RateLimitMiddleware(
            app=app,
            requests_per_minute=60,
            requests_per_second=10
        )
        assert middleware.requests_per_minute == 60
        assert middleware.requests_per_second == 10
    
    def test_client_id_extraction_api_key(self):
        """Test client ID extraction with API key"""
        app = MagicMock()
        middleware = RateLimitMiddleware(app=app)
        
        mock_request = MagicMock()
        mock_request.headers.get.return_value = "test-api-key-12345678"
        
        client_id = middleware._get_client_id(mock_request)
        assert "api_key:" in client_id
    
    def test_client_id_extraction_ip(self):
        """Test client ID extraction with IP address"""
        app = MagicMock()
        middleware = RateLimitMiddleware(app=app)
        
        mock_request = MagicMock()
        mock_request.headers.get.return_value = None
        mock_request.client.host = "192.168.1.1"
        
        client_id = middleware._get_client_id(mock_request)
        assert "ip:192.168.1.1" == client_id


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
