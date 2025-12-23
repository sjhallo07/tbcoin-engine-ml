# models/contract_models.py
# NOTE: These models are for future phases and are not part of Phase 1 schema.
# They are not currently used in the application.

from sqlalchemy import Column, Integer, String, DateTime, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

# New: cross-chain contract models (Pydantic) for EVM ERC-20, Solana SPL, and Sui Move
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator

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


# =====================
# Cross-chain models (runtime schemas, non-DB)
# =====================

class ChainType(str, Enum):
    evm = "evm"
    solana = "solana"
    sui = "sui"


class EthereumNetwork(str, Enum):
    mainnet = "mainnet"
    sepolia = "sepolia"
    holesky = "holesky"


class SolanaCluster(str, Enum):
    mainnet_beta = "mainnet-beta"
    devnet = "devnet"
    testnet = "testnet"


class SuiNetwork(str, Enum):
    mainnet = "mainnet"
    testnet = "testnet"
    devnet = "devnet"


class BaseContract(BaseModel):
    """Base runtime schema for a blockchain contract/token descriptor.

    These models are used for request/response validation and internal coordination,
    not persisted to SQL tables. They complement the future-phase SQLAlchemy models above.
    """

    chain: ChainType = Field(..., description="Blockchain family: evm | solana | sui")
    name: Optional[str] = Field(None, description="Human-readable name")
    description: Optional[str] = Field(None, description="Optional description")


class ERC20Contract(BaseContract):
    """ERC-20 (EVM) token contract metadata."""

    chain: ChainType = Field(default=ChainType.evm, frozen=True)
    address: str = Field(..., description="EIP-55 address of the token contract")
    network: EthereumNetwork = Field(default=EthereumNetwork.mainnet)
    symbol: str = Field(...)
    decimals: int = Field(default=18, ge=0, le=36)
    abi: Optional[List[dict]] = Field(
        default=None,
        description="Optional contract ABI entries (when direct method encoding is needed)")

    @field_validator("address")
    @classmethod
    def validate_evm_address(cls, v: str) -> str:
        try:
            from web3 import Web3
            if Web3.is_address(v):
                return Web3.to_checksum_address(v)
        except Exception:
            # Fallback: basic shape check if web3 is unavailable
            pass
        if isinstance(v, str) and v.startswith("0x") and len(v) == 42:
            return v
        raise ValueError("Invalid EVM address format")


class SPLTokenContract(BaseContract):
    """Solana SPL token mint metadata."""

    chain: ChainType = Field(default=ChainType.solana, const=True)
    mint: str = Field(..., description="Base58 mint public key")
    symbol: str = Field(...)
    decimals: int = Field(..., ge=0, le=36)
    cluster: SolanaCluster = Field(default=SolanaCluster.devnet)
    program_id: Optional[str] = Field(
        default="TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
        description="SPL token program ID (default: v1)")

    @field_validator("mint")
    @classmethod
    def validate_solana_pubkey(cls, v: str) -> str:
        try:
            from solana.publickey import PublicKey
            # Will raise if invalid
            _ = PublicKey(v)
            return v
        except Exception:
            # Basic sanity: typical Base58 length for pubkeys ~ 32-44 chars
            if isinstance(v, str) and 32 <= len(v) <= 64:
                return v
            raise ValueError("Invalid Solana mint public key")


class SuiMoveContract(BaseContract):
    """Sui Move coin/contract metadata."""

    chain: ChainType = Field(default=ChainType.sui, const=True)
    package_id: str = Field(..., description="0x-prefixed package ID")
    module: str = Field(..., description="Move module name")
    type: str = Field(..., description="Full type e.g., 0x2::sui::SUI or custom coin type")
    symbol: str = Field(...)
    decimals: int = Field(..., ge=0, le=36)
    network: SuiNetwork = Field(default=SuiNetwork.testnet)

    @field_validator("package_id")
    @classmethod
    def validate_sui_package(cls, v: str) -> str:
        if isinstance(v, str) and v.startswith("0x") and len(v) >= 3:
            # Minimal hex check
            try:
                int(v[2:], 16)
                return v
            except Exception:
                pass
        raise ValueError("Invalid Sui package_id (expect 0x-prefixed hex)")

    @field_validator("module")
    @classmethod
    def validate_module(cls, v: str) -> str:
        if not v or not v.replace("_", "").isalnum():
            raise ValueError("Invalid Move module identifier")
        return v

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        # Heuristic: expecting something like 0x...::module::Type
        if "::" not in v:
            raise ValueError("Invalid Move type; expected 'pkg::module::Type'")
        return v


# Convenience method call schemas (optional, non-persistent)

class ERC20TransferCall(BaseModel):
    from_address: str
    to_address: str
    amount: int = Field(..., ge=0)

    @field_validator("from_address", "to_address")
    @classmethod
    def _validate_evm_addr(cls, v: str) -> str:
        try:
            from web3 import Web3
            if Web3.is_address(v):
                return Web3.to_checksum_address(v)
        except Exception:
            pass
        if isinstance(v, str) and v.startswith("0x") and len(v) == 42:
            return v
        raise ValueError("Invalid EVM address format")


class SPLTransferCall(BaseModel):
    from_owner: str
    to_owner: str
    amount: int = Field(..., ge=0)
    decimals: Optional[int] = Field(None, ge=0, le=36)

    @field_validator("from_owner", "to_owner")
    @classmethod
    def _validate_solana_owner(cls, v: str) -> str:
        try:
            from solana.publickey import PublicKey
            _ = PublicKey(v)
            return v
        except Exception:
            if isinstance(v, str) and 32 <= len(v) <= 64:
                return v
            raise ValueError("Invalid Solana owner public key")


class SuiMoveCall(BaseModel):
    package_id: str
    module: str
    function: str
    type_arguments: List[str] = Field(default_factory=list)
    arguments: List[str] = Field(default_factory=list)

    @field_validator("package_id")
    @classmethod
    def _validate_pkg(cls, v: str) -> str:
        if isinstance(v, str) and v.startswith("0x"):
            try:
                int(v[2:], 16)
                return v
            except Exception:
                pass
        raise ValueError("Invalid Sui package_id (0x-hex expected)")

    @field_validator("module", "function")
    @classmethod
    def _validate_ident(cls, v: str) -> str:
        if not v or not v.replace("_", "").isalnum():
            raise ValueError("Invalid Move identifier")
        return v


__all__ = [
    "ContractDeployment",
    "ContractInteraction",
    "ChainEvent",
    # runtime models
    "ChainType",
    "EthereumNetwork",
    "SolanaCluster",
    "SuiNetwork",
    "BaseContract",
    "ERC20Contract",
    "SPLTokenContract",
    "SuiMoveContract",
    "ERC20TransferCall",
    "SPLTransferCall",
    "SuiMoveCall",
]