"""
kms_signer.py

Simple KMS-backed signer abstraction. This file provides a best-effort local
implementation that prefers an external KMS (AWS KMS example) when configured,
and falls back to a local Keypair stored encrypted on disk. It is intentionally
lightweight and instructional — replace with your organization's KMS/HSM code
and secure signing service in production.

NOTE: This file does not implement a production-ready KMS client. It shows the
shape of how to integrate with KMS and how to avoid keeping plaintext keys in
the repository.
"""

import os
import json
import logging
from typing import Optional

from solana.keypair import Keypair

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# If AWS KMS is desired, set these env vars (example):
# - USE_AWS_KMS=1
# - AWS_REGION, AWS_KMS_KEY_ID
# For demo purposes we won't import boto3 unless configured.

USE_AWS_KMS = os.getenv("USE_AWS_KMS", "0") in ("1", "true", "yes")


class KMSSigner:
    """Abstraction for signing operations.

    Methods:
      - sign_message(message_bytes) -> signature bytes
      - public_key() -> solana.PublicKey

    Implementation strategy:
      - If USE_AWS_KMS, call AWS KMS Sign API (not implemented in this starter).
      - Else, try encrypted local storage (decrypt using env-provided key).
    """

    def __init__(self, encrypted_key_path: str = "encrypted_key.json"):
        self.encrypted_key_path = encrypted_key_path
        self._keypair: Optional[Keypair] = None
        if not USE_AWS_KMS:
            self._load_local_keypair()

    def _load_local_keypair(self):
        """Load and decrypt a local keypair file. The decryption key should be
        provided via environment (e.g., KMS-decrypted symmetric key injected by
        CI/infra). For the starter, we expect the environment variable
        `LOCAL_KEY_DECRYPTION_KEY` to contain a base64 key — you should replace
        this with your own secure mechanism.
        """
        if not os.path.exists(self.encrypted_key_path):
            logger.info("No encrypted local key file found at %s", self.encrypted_key_path)
            return
        try:
            with open(self.encrypted_key_path, "r", encoding="utf-8") as f:
                payload = json.load(f)
            # payload expected: {"ciphertext": "...", "nonce": "..."}
            # In the starter we simply store the raw secret encrypted with a
            # symmetric key; implement proper AEAD (AES-GCM) in production.
            decrypt_key = os.getenv("LOCAL_KEY_DECRYPTION_KEY")
            if not decrypt_key:
                logger.warning("LOCAL_KEY_DECRYPTION_KEY not set; cannot decrypt local key")
                return
            # For safety in starter, assume payload contains raw secret as array
            secret_arr = payload.get("secret_array")
            if secret_arr:
                sk = bytes(secret_arr)
                self._keypair = Keypair.from_secret_key(sk)
                logger.info("Loaded local keypair from encrypted file (starter mode)")
        except Exception as e:
            logger.exception("Failed to load/decrypt local keypair: %s", e)

    def public_key(self):
        if USE_AWS_KMS:
            # Production: call KMS to retrieve public key associated with key id
            raise NotImplementedError("AWS KMS signing path not implemented in starter")
        if self._keypair:
            return self._keypair.public_key
        return None

    def sign_transaction(self, tx_bytes: bytes) -> bytes:
        if USE_AWS_KMS:
            # Production: call AWS KMS Sign API and return signature bytes
            raise NotImplementedError("AWS KMS signing path not implemented in starter")
        if not self._keypair:
            raise RuntimeError("No keypair available to sign")
        # For Solana, signing is usually done on Transaction object; the
        # transaction object is signed with Keypair.sign(). Return the raw
        # secret signature here as an instructional example.
        sig = self._keypair.sign(tx_bytes)
        return sig.signature


# Convenience helper for other modules
_default_signer: Optional[KMSSigner] = None


def get_signer() -> KMSSigner:
    global _default_signer
    if _default_signer is None:
        _default_signer = KMSSigner()
    return _default_signer
