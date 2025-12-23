"""ORM models mapped to Database Schema for Phase 1."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, Column, DateTime, DECIMAL, Integer, JSON, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_hash = Column(String(255), unique=True, nullable=False, index=True)
    chain = Column(String(50), nullable=False)
    block_number = Column(BigInteger, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    wallet_address = Column(String(255), nullable=False, index=True)
    from_address = Column(String(255))
    to_address = Column(String(255))
    value = Column(DECIMAL(36, 18))
    token_address = Column(String(255))
    gas_used = Column(DECIMAL(18, 8))
    gas_price = Column(DECIMAL(18, 8))
    status = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)


class WalletBehavior(Base):
    __tablename__ = "wallet_behavior"

    id = Column(Integer, primary_key=True, index=True)
    wallet_address = Column(String(255), unique=True, nullable=False, index=True)
    total_transactions = Column(Integer, default=0)
    total_volume = Column(DECIMAL(36, 18), default=0)
    avg_transaction_size = Column(DECIMAL(36, 18))
    first_transaction = Column(DateTime)
    last_transaction = Column(DateTime)
    wallet_age_days = Column(Integer)
    behavior_cluster = Column(Integer)
    risk_score = Column(DECIMAL(5, 4))
    updated_at = Column(DateTime, default=datetime.utcnow)


class ModelPrediction(Base):
    __tablename__ = "model_predictions"

    id = Column(Integer, primary_key=True, index=True)
    model_type = Column(String(100), nullable=False)
    prediction_type = Column(String(100), nullable=False)
    input_features = Column(JSON)
    prediction_output = Column(JSON)
    confidence = Column(DECIMAL(5, 4))
    timestamp = Column(DateTime, default=datetime.utcnow)
    actual_outcome = Column(JSON)


class FeatureStore(Base):
    __tablename__ = "feature_store"

    id = Column(Integer, primary_key=True, index=True)
    feature_set_name = Column(String(255), nullable=False)
    wallet_address = Column(String(255))
    timestamp = Column(DateTime, nullable=False)
    features = Column(JSON, nullable=False)
    label = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
