"""Pydantic schemas for TB Coin Engine ML

This module defines all data models/schemas used throughout the application.
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator
import re


# ============================================================================
# Health Models
# ============================================================================

class HealthStatus(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Current health status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    services: Dict[str, str] = Field(default_factory=dict)


# ============================================================================
# Transaction Models
# ============================================================================

class TransactionStatus(str, Enum):
    """Transaction status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TransactionType(str, Enum):
    """Transaction type enumeration"""
    SEND = "send"
    RECEIVE = "receive"
    MINT = "mint"
    BURN = "burn"
    STAKE = "stake"
    UNSTAKE = "unstake"
    SWAP = "swap"


class TransactionRequest(BaseModel):
    """Transaction request model with validation"""
    from_user: str = Field(..., min_length=1, max_length=100)
    to_user: str = Field(..., min_length=1, max_length=100)
    amount: float = Field(..., gt=0)
    transaction_type: TransactionType = TransactionType.SEND
    metadata: Optional[Dict[str, Any]] = None

    @field_validator('from_user', 'to_user')
    @classmethod
    def sanitize_user_id(cls, v: str) -> str:
        """Sanitize user IDs to prevent injection attacks"""
        # Remove any special characters except alphanumeric, dash, underscore
        sanitized = re.sub(r'[^a-zA-Z0-9_-]', '', v)
        if not sanitized:
            raise ValueError("User ID must contain valid characters")
        return sanitized


class Transaction(BaseModel):
    """Transaction model"""
    transaction_id: str = Field(..., description="Unique transaction identifier")
    from_user: str = Field(..., description="Sender user ID")
    to_user: str = Field(..., description="Receiver user ID")
    amount: float = Field(..., gt=0, description="Transaction amount")
    transaction_type: TransactionType = Field(..., description="Type of transaction")
    status: TransactionStatus = Field(default=TransactionStatus.PENDING)
    fee: float = Field(default=0, ge=0, description="Transaction fee")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        """Pydantic model configuration"""
        from_attributes = True


# ============================================================================
# Coin Models
# ============================================================================

class CoinBalance(BaseModel):
    """User coin balance model"""
    user_id: str = Field(..., description="User identifier")
    balance: float = Field(default=0, ge=0, description="Available balance")
    staked_balance: float = Field(default=0, ge=0, description="Staked balance")
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic model configuration"""
        from_attributes = True


# ============================================================================
# User and Authentication Models
# ============================================================================

class UserRole(str, Enum):
    """User role enumeration for RBAC"""
    ADMIN = "admin"
    USER = "user"
    OPERATOR = "operator"
    VIEWER = "viewer"


class UserBase(BaseModel):
    """Base user model"""
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    role: UserRole = Field(default=UserRole.USER)
    is_active: bool = Field(default=True)

    @field_validator('username')
    @classmethod
    def sanitize_username(cls, v: str) -> str:
        """Sanitize username to prevent injection"""
        sanitized = re.sub(r'[^a-zA-Z0-9_-]', '', v)
        if len(sanitized) < 3:
            raise ValueError("Username must be at least 3 valid characters")
        return sanitized

    @field_validator('email')
    @classmethod
    def sanitize_email(cls, v: str) -> str:
        """Sanitize email to prevent injection"""
        # Remove potentially dangerous characters
        sanitized = v.strip().lower()
        if '<' in sanitized or '>' in sanitized or ';' in sanitized:
            raise ValueError("Invalid email format")
        return sanitized


class UserCreate(UserBase):
    """User creation model"""
    password: str = Field(..., min_length=8)

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r'[A-Z]', v):
            raise ValueError("Password must contain an uppercase letter")
        if not re.search(r'[a-z]', v):
            raise ValueError("Password must contain a lowercase letter")
        if not re.search(r'\d', v):
            raise ValueError("Password must contain a digit")
        return v


class User(UserBase):
    """User response model"""
    id: str = Field(..., description="Unique user identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Config:
        """Pydantic model configuration"""
        from_attributes = True


class UserInDB(User):
    """User model stored in database"""
    hashed_password: str


class Token(BaseModel):
    """JWT token response model"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Expiration time in seconds")


class TokenData(BaseModel):
    """Token payload data"""
    sub: str = Field(..., description="Subject (user ID)")
    role: UserRole = Field(default=UserRole.USER)
    exp: Optional[datetime] = None


# ============================================================================
# Job Models for Coin Engine
# ============================================================================

class JobStatus(str, Enum):
    """Job execution status"""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobType(str, Enum):
    """Types of jobs the coin engine can execute"""
    TRANSACTION = "transaction"
    ANALYSIS = "analysis"
    ML_PREDICTION = "ml_prediction"
    BLOCKCHAIN_SYNC = "blockchain_sync"
    DATA_PROCESSING = "data_processing"
    SMART_CONTRACT = "smart_contract"
    STAKING = "staking"


class JobCreate(BaseModel):
    """Job creation model"""
    job_type: JobType = Field(..., description="Type of job to execute")
    priority: int = Field(default=5, ge=1, le=10, description="Job priority (1-10)")
    payload: Dict[str, Any] = Field(default_factory=dict)
    callback_url: Optional[str] = None

    @field_validator('payload')
    @classmethod
    def validate_payload(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize job payload"""
        # Remove any keys with potentially dangerous values
        sanitized = {}
        for key, value in v.items():
            # Sanitize string keys
            clean_key = re.sub(r'[^a-zA-Z0-9_]', '', str(key))
            if clean_key:
                if isinstance(value, str):
                    # Basic XSS prevention for string values
                    sanitized[clean_key] = re.sub(r'<[^>]*>', '', value)
                else:
                    sanitized[clean_key] = value
        return sanitized


class Job(BaseModel):
    """Job model"""
    job_id: str = Field(..., description="Unique job identifier")
    job_type: JobType = Field(..., description="Type of job")
    status: JobStatus = Field(default=JobStatus.PENDING)
    priority: int = Field(default=5, ge=1, le=10)
    payload: Dict[str, Any] = Field(default_factory=dict)
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    callback_url: Optional[str] = None
    created_by: Optional[str] = None

    class Config:
        """Pydantic model configuration"""
        from_attributes = True


# ============================================================================
# ML Action Models
# ============================================================================

class MLActionRequest(BaseModel):
    """ML action request model"""
    action_type: str = Field(..., description="Type of ML action to perform")
    user_id: str = Field(..., min_length=1, max_length=100)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    use_llm: bool = Field(default=False, description="Whether to use LLM for processing")
    
    @field_validator('action_type')
    @classmethod
    def validate_action_type(cls, v: str) -> str:
        """Validate and sanitize action type"""
        valid_actions = ["analyze", "recommend", "predict", "optimize", "transfer"]
        sanitized = v.lower().strip()
        if sanitized not in valid_actions:
            raise ValueError(f"Invalid action type. Must be one of: {valid_actions}")
        return sanitized
    
    @field_validator('user_id')
    @classmethod
    def sanitize_user_id(cls, v: str) -> str:
        """Sanitize user ID"""
        sanitized = re.sub(r'[^a-zA-Z0-9_-]', '', v)
        if not sanitized:
            raise ValueError("User ID must contain valid characters")
        return sanitized


class MLActionResponse(BaseModel):
    """ML action response model"""
    success: bool = Field(default=True)
    action_type: str
    result: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(default=0.0, ge=0, le=1)
    reasoning: Optional[str] = None
    recommendations: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# ML Prediction Models
# ============================================================================

class PredictionRequest(BaseModel):
    """ML prediction request model"""
    model_type: str = Field(..., min_length=1, max_length=50)
    features: Dict[str, Any] = Field(default_factory=dict)
    include_explanation: bool = Field(default=False)

    @field_validator('model_type')
    @classmethod
    def sanitize_model_type(cls, v: str) -> str:
        """Sanitize model type name"""
        sanitized = re.sub(r'[^a-zA-Z0-9_-]', '', v)
        if not sanitized:
            raise ValueError("Model type must contain valid characters")
        return sanitized


class PredictionResponse(BaseModel):
    """ML prediction response model"""
    prediction: Any
    confidence: float = Field(ge=0, le=1)
    model_version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    explanation: Optional[Dict[str, Any]] = None


# ============================================================================
# Error Response Models
# ============================================================================

class ErrorDetail(BaseModel):
    """Detailed error information"""
    code: str
    message: str
    field: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standard error response model"""
    status: str = "error"
    message: str
    details: Optional[List[ErrorDetail]] = None
    request_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
