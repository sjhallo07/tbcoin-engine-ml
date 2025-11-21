from __future__ import annotations

import logging
import os
import re
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

try:  # pragma: no cover - optional dependency
    import jwt
except ImportError:  # pragma: no cover
    jwt = None  # type: ignore

try:  # pragma: no cover - optional dependency
    from web3 import Web3 as _Web3Module
except ImportError:  # pragma: no cover
    _Web3Module = None  # type: ignore


_WEB3_AVAILABLE = _Web3Module is not None


def _is_address(address: str) -> bool:
    if _WEB3_AVAILABLE:  # pragma: no cover - heavy dependency
        assert _Web3Module is not None
        return bool(_Web3Module.is_address(address))
    return isinstance(address, str) and address.startswith("0x") and len(address) == 42


def _to_checksum(address: str) -> str:
    if _WEB3_AVAILABLE:  # pragma: no cover
        assert _Web3Module is not None
        return _Web3Module.to_checksum_address(address)
    return address


LOGGER = logging.getLogger(__name__)


@dataclass
class AuthenticationContext:
    """Represents the outcome of an authentication attempt."""

    subject: str
    scopes: List[str]
    issued_at: float
    expires_at: float


class AuthenticationError(RuntimeError):
    pass


class AuthenticationMiddleware:
    """JWT-based authentication with rate limiting and audit logging."""

    def __init__(self, secret: str, *, rate_limit: int = 120, window_seconds: int = 60) -> None:
        if not secret:
            raise AuthenticationError("JWT secret not configured")
        self._secret = secret
        self._rate_limit = rate_limit
        self._window_seconds = window_seconds
        self._audit_logger = logging.getLogger("AuthenticationAudit")
        self._request_windows: Dict[str, List[float]] = {}

    def authenticate(self, token: str) -> AuthenticationContext:
        if jwt is None:  # pragma: no cover
            raise AuthenticationError("PyJWT is required for authentication")
        claims = jwt.decode(token, self._secret, algorithms=["HS256"])
        subject = claims.get("sub")
        if not subject:
            raise AuthenticationError("JWT subject missing")
        self._enforce_rate_limit(subject)
        context = AuthenticationContext(
            subject=subject,
            scopes=claims.get("scopes", []),
            issued_at=float(claims.get("iat", time.time())),
            expires_at=float(claims.get("exp", time.time() + 3600)),
        )
        self._audit_logger.info("Auth success for %s", subject)
        return context

    def _enforce_rate_limit(self, subject: str) -> None:
        now = time.time()
        window_start = now - self._window_seconds
        bucket = self._request_windows.setdefault(subject, [])
        bucket[:] = [ts for ts in bucket if ts >= window_start]
        if len(bucket) >= self._rate_limit:
            raise AuthenticationError("Rate limit exceeded")
        bucket.append(now)


class SecurityManager:
    """Centralizes contract validation, authentication, and auditing."""

    def __init__(self, *, logger: Optional[logging.Logger] = None) -> None:
        self._logger = logger or logging.getLogger(self.__class__.__name__)

    def validate_smart_contract(self, contract_address: str, abi: List[Any]) -> bool:
        if not contract_address:
            self._logger.error("Contract address not provided")
            return False
        if not _WEB3_AVAILABLE:
            self._logger.warning("web3.py not installed; skipping deep contract validation")
            return True
        if not _is_address(contract_address):
            self._logger.error("Invalid contract address: %s", contract_address)
            return False
        suspicious_patterns = {"delegatecall", "selfdestruct", "tx.origin"}
        serialized_abi = " ".join(str(item).lower() for item in abi)
        if any(pattern in serialized_abi for pattern in suspicious_patterns):
            self._logger.warning("Potentially dangerous construct detected in ABI")
            return False
        if not self._verify_contract_source(contract_address):
            self._logger.warning("Contract source verification failed")
            return False
        return True

    def secure_api_authentication(self) -> AuthenticationMiddleware:
        secret = os.getenv("API_JWT_SECRET", "")
        middleware = AuthenticationMiddleware(secret)
        return middleware

    def _verify_contract_source(self, contract_address: str) -> bool:
        if not _WEB3_AVAILABLE:
            return True
        checksum = _to_checksum(contract_address)
        pattern = re.compile(r"^0x[0-9a-fA-F]{40}$")
        if not pattern.match(checksum):
            return False
        return True
