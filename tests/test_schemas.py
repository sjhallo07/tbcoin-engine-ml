"""
Tests for Pydantic schemas and input validation
Run with: python -m pytest tests/test_schemas.py -v
"""
import pytest
from datetime import datetime
from pydantic import ValidationError

from app.models.schemas import (
    HealthStatus,
    CoinBalance,
    Transaction,
    TransactionRequest,
    TransactionStatus,
    TransactionType,
    User,
    UserCreate,
    UserRole,
    Job,
    JobCreate,
    JobStatus,
    JobType,
    MLActionRequest,
    MLActionResponse,
)


class TestHealthStatus:
    """Test HealthStatus schema"""
    
    def test_health_status_creation(self):
        """Test creating a valid HealthStatus"""
        status = HealthStatus(
            status="healthy",
            version="1.0.0",
            services={"api": "operational"}
        )
        assert status.status == "healthy"
        assert status.version == "1.0.0"
        assert status.services["api"] == "operational"
    
    def test_health_status_default_timestamp(self):
        """Test that timestamp is auto-generated"""
        status = HealthStatus(status="healthy", version="1.0.0")
        assert isinstance(status.timestamp, datetime)


class TestCoinBalance:
    """Test CoinBalance schema"""
    
    def test_coin_balance_creation(self):
        """Test creating a valid CoinBalance"""
        balance = CoinBalance(
            user_id="user123",
            balance=100.50,
            staked_balance=25.0
        )
        assert balance.user_id == "user123"
        assert balance.balance == 100.50
        assert balance.staked_balance == 25.0
    
    def test_coin_balance_defaults(self):
        """Test CoinBalance default values"""
        balance = CoinBalance(user_id="user123")
        assert balance.balance == 0
        assert balance.staked_balance == 0


class TestTransactionRequest:
    """Test TransactionRequest schema with validation"""
    
    def test_valid_transaction_request(self):
        """Test creating a valid TransactionRequest"""
        request = TransactionRequest(
            from_user="user1",
            to_user="user2",
            amount=100.0
        )
        assert request.from_user == "user1"
        assert request.to_user == "user2"
        assert request.amount == 100.0
    
    def test_user_id_sanitization(self):
        """Test that user IDs are sanitized"""
        request = TransactionRequest(
            from_user="user1_test-123",
            to_user="user2",
            amount=50.0
        )
        assert request.from_user == "user1_test-123"
    
    def test_invalid_user_id_special_chars(self):
        """Test that special characters in user ID are removed"""
        request = TransactionRequest(
            from_user="user<script>alert(1)</script>",
            to_user="user2",
            amount=50.0
        )
        # Special characters should be stripped
        assert "<" not in request.from_user
        assert ">" not in request.from_user
    
    def test_invalid_amount_zero(self):
        """Test that zero amount is rejected"""
        with pytest.raises(ValidationError):
            TransactionRequest(
                from_user="user1",
                to_user="user2",
                amount=0
            )
    
    def test_invalid_amount_negative(self):
        """Test that negative amount is rejected"""
        with pytest.raises(ValidationError):
            TransactionRequest(
                from_user="user1",
                to_user="user2",
                amount=-100
            )


class TestUserCreate:
    """Test UserCreate schema with password validation"""
    
    def test_valid_user_creation(self):
        """Test creating a valid user"""
        user = UserCreate(
            username="testuser",
            email="test@example.com",
            password="SecurePass123"
        )
        assert user.username == "testuser"
        assert user.email == "test@example.com"
    
    def test_password_too_short(self):
        """Test that short password is rejected"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="testuser",
                email="test@example.com",
                password="short"
            )
        assert "8 characters" in str(exc_info.value)
    
    def test_password_missing_uppercase(self):
        """Test that password without uppercase is rejected"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="testuser",
                email="test@example.com",
                password="lowercase123"
            )
        assert "uppercase" in str(exc_info.value).lower()
    
    def test_password_missing_digit(self):
        """Test that password without digit is rejected"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="testuser",
                email="test@example.com",
                password="SecurePassword"
            )
        assert "digit" in str(exc_info.value).lower()
    
    def test_invalid_email_format(self):
        """Test that invalid email is rejected"""
        with pytest.raises(ValidationError):
            UserCreate(
                username="testuser",
                email="not-an-email",
                password="SecurePass123"
            )
    
    def test_username_sanitization(self):
        """Test that username is sanitized"""
        user = UserCreate(
            username="test_user-123",
            email="test@example.com",
            password="SecurePass123"
        )
        assert user.username == "test_user-123"


class TestJobCreate:
    """Test JobCreate schema with validation"""
    
    def test_valid_job_creation(self):
        """Test creating a valid job"""
        job = JobCreate(
            job_type=JobType.TRANSACTION,
            priority=8,
            payload={"key": "value"}
        )
        assert job.job_type == JobType.TRANSACTION
        assert job.priority == 8
    
    def test_priority_bounds(self):
        """Test that priority is within bounds"""
        with pytest.raises(ValidationError):
            JobCreate(
                job_type=JobType.ANALYSIS,
                priority=11  # Max is 10
            )
    
    def test_payload_sanitization(self):
        """Test that payload is sanitized for XSS"""
        job = JobCreate(
            job_type=JobType.DATA_PROCESSING,
            payload={"name": "<script>alert(1)</script>test"}
        )
        # Script tags should be removed from string values
        assert "<script>" not in job.payload.get("name", "")


class TestMLActionRequest:
    """Test MLActionRequest schema"""
    
    def test_valid_action_request(self):
        """Test creating a valid ML action request"""
        request = MLActionRequest(
            action_type="analyze",
            user_id="user123",
            parameters={"amount": 100},
            use_llm=True
        )
        assert request.action_type == "analyze"
        assert request.user_id == "user123"
        assert request.use_llm is True
    
    def test_invalid_action_type(self):
        """Test that invalid action type is rejected"""
        with pytest.raises(ValidationError):
            MLActionRequest(
                action_type="invalid_action",
                user_id="user123"
            )
    
    def test_action_type_normalization(self):
        """Test that action type is normalized to lowercase"""
        request = MLActionRequest(
            action_type="ANALYZE",
            user_id="user123"
        )
        assert request.action_type == "analyze"


class TestEnumerations:
    """Test enumeration values"""
    
    def test_transaction_status_values(self):
        """Test TransactionStatus enum values"""
        assert TransactionStatus.PENDING == "pending"
        assert TransactionStatus.COMPLETED == "completed"
        assert TransactionStatus.FAILED == "failed"
    
    def test_transaction_type_values(self):
        """Test TransactionType enum values"""
        assert TransactionType.SEND == "send"
        assert TransactionType.MINT == "mint"
        assert TransactionType.STAKE == "stake"
    
    def test_user_role_values(self):
        """Test UserRole enum values"""
        assert UserRole.ADMIN == "admin"
        assert UserRole.USER == "user"
        assert UserRole.OPERATOR == "operator"
    
    def test_job_status_values(self):
        """Test JobStatus enum values"""
        assert JobStatus.PENDING == "pending"
        assert JobStatus.RUNNING == "running"
        assert JobStatus.COMPLETED == "completed"
    
    def test_job_type_values(self):
        """Test JobType enum values"""
        assert JobType.TRANSACTION == "transaction"
        assert JobType.ML_PREDICTION == "ml_prediction"
        assert JobType.BLOCKCHAIN_SYNC == "blockchain_sync"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
