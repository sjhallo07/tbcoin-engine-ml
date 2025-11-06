# models/contract_models.py
# NOTE: These models are for future phases and are not part of Phase 1 schema.
# They are not currently used in the application.

from sqlalchemy import Column, Integer, String, DateTime, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class ContractDeployment(Base):
    """Contract deployment model - Reserved for future phases."""
    __tablename__ = "contract_deployments"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    chain = Column(String(50), nullable=False)
    contract_address = Column(String(255), unique=True, nullable=False)
    code_hash = Column(String(255), nullable=False)
    contract_name = Column(String(255), nullable=False)
    deployer_address = Column(String(255), nullable=False)
    artifact_metadata = Column(JSON, nullable=True)
    deployment_tx_hash = Column(String(255), nullable=False)
    block_number = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
class ContractInteraction(Base):
    """Contract interaction model - Reserved for future phases."""
    __tablename__ = "contract_interactions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    deployment_id = Column(String(36), nullable=False)
    tx_hash = Column(String(255), nullable=False)
    message_name = Column(String(255), nullable=False)
    arguments = Column(JSON, nullable=True)
    caller_address = Column(String(255), nullable=False)
    gas_used = Column(Integer, nullable=True)
    storage_deposit = Column(Integer, nullable=True)
    success = Column(Integer, nullable=False)  # 0 or 1
    error_message = Column(Text, nullable=True)
    block_number = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
class ChainEvent(Base):
    """Chain event model - Reserved for future phases."""
    __tablename__ = "chain_events"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    chain = Column(String(50), nullable=False)
    contract_address = Column(String(255), nullable=False)
    event_name = Column(String(255), nullable=False)
    event_data = Column(JSON, nullable=True)
    block_number = Column(Integer, nullable=False)
    tx_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)