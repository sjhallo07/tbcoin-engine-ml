"""Minimal Solana adapter utilities.

This module provides a small wrapper around `solana` (solana-py) RPC client for
basic operations: balance queries, account info, airdrops (devnet), and sending
transactions. It's intentionally lightweight and guarded so the rest of the repo
can import it without heavy ML dependencies.

Note: Sending real transactions requires a signer. For production use a KMS/HSM
signer; for local development you can pass a local Keypair (dev only).
"""
from typing import Any, Dict, Optional
import os

try:
    from solana.rpc.api import Client
    from solana.publickey import PublicKey
    from solana.transaction import Transaction
    from solana.rpc.types import TxOpts
    SOLANA_AVAILABLE = True
except Exception:  # pragma: no cover - optional dependency
    # Keep module import-safe even if solana isn't installed.
    Client = None  # type: ignore
    PublicKey = None  # type: ignore
    Transaction = None  # type: ignore
    TxOpts = None  # type: ignore
    SOLANA_AVAILABLE = False


class SolanaAdapter:
    """A tiny wrapper around the solana RPC client.

    Usage:
        adapter = SolanaAdapter(os.getenv("SOLANA_RPC_URL", "https://api.devnet.solana.com"))
        adapter.get_balance("YourPubkeyHere")
    """

    def __init__(self, rpc_url: Optional[str] = None):
        self.rpc_url = rpc_url or os.getenv("SOLANA_RPC_URL", "https://api.devnet.solana.com")
        if SOLANA_AVAILABLE:
            self.client = Client(self.rpc_url)
        else:
            self.client = None

    def is_available(self) -> bool:
        return SOLANA_AVAILABLE and self.client is not None

    def get_balance(self, pubkey: str) -> Dict[str, Any]:
        """Return balance (in lamports) for a pubkey.

        Returns a dict with the raw RPC result under `result` key when available.
        """
        if not self.is_available():
            return {"error": "solana package not installed"}
        pk = PublicKey(pubkey)
        return self.client.get_balance(pk)

    def get_account_info(self, pubkey: str) -> Dict[str, Any]:
        if not self.is_available():
            return {"error": "solana package not installed"}
        pk = PublicKey(pubkey)
        return self.client.get_account_info(pk)

    def request_airdrop(self, pubkey: str, lamports: int = 1000000000) -> Dict[str, Any]:
        """Request airdrop (devnet/test-only)."""
        if not self.is_available():
            return {"error": "solana package not installed"}
        pk = PublicKey(pubkey)
        return self.client.request_airdrop(pk, lamports)

    def send_transaction(self, transaction: Any, signer: Any, opts: Optional[TxOpts] = None) -> Dict[str, Any]:
        """Send a Transaction object using the provided signer.

        signer should be a Keypair-like object with `public_key` and `sign` capabilities
        (for local dev) or a wrapper that signs via KMS in production. This method is
        intentionally minimal — real-world usage should handle retries, confirmation
        strategies and idempotency.
        """
        if not self.is_available():
            return {"error": "solana package not installed"}
        # The caller is responsible for creating and populating a Transaction
        tx = transaction
        # If signer has a .public_key attribute the client can send the tx
        try:
            resp = self.client.send_transaction(tx, signer, opts=opts)  # type: ignore
            return resp
        except Exception as exc:
            return {"error": str(exc)}


__all__ = ["SolanaAdapter"]
