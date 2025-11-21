"""Thin wrapper around grafana_api for querying Grafana.

This module is intentionally defensive: if grafana_api is not installed (e.g.
Python 3.14 environment without pinned ML/monitoring stack), the public class
still loads but methods return informative error payloads instead of raising.
"""

from __future__ import annotations

from typing import Any, Dict, Optional
import os

try:  # Runtime optional dependency
    from grafana_api.grafana_face import GrafanaFace  # type: ignore
except Exception:  # pragma: no cover - absence guard
    GrafanaFace = None  # type: ignore


class GrafanaClient:
    """Wrapper providing minimal Grafana interactions used by the API.

    Reads configuration from environment variables:
      GRAFANA_HOST (required for live calls)
      GRAFANA_API_KEY (token)
      GRAFANA_PROTOCOL (default: https)
      GRAFANA_PORT (default: 443)
    """

    def __init__(
        self,
        host: Optional[str] | None = None,
        api_key: Optional[str] | None = None,
        protocol: str = "https",
        port: int = 443,
    ) -> None:
        self.host = host or os.getenv("GRAFANA_HOST")
        self.api_key = api_key or os.getenv("GRAFANA_API_KEY")
        self.protocol = os.getenv("GRAFANA_PROTOCOL", protocol)
        self.port = int(os.getenv("GRAFANA_PORT", str(port)))
        self._client: Optional[Any] = None
        self._init_client()

    def _init_client(self) -> None:
        if GrafanaFace and self.host and self.api_key:
            try:
                self._client = GrafanaFace(
                    auth=("api_key", self.api_key),
                    host=self.host,
                    protocol=self.protocol,
                    port=self.port,
                )
            except Exception as exc:  # pragma: no cover - network/env issues
                self._client = None
                self._last_error = f"grafana init failed: {exc}"  # type: ignore
        else:
            self._client = None

    def availability(self) -> Dict[str, Any]:
        """Report if grafana_api is importable and configured."""
        return {
            "installed": GrafanaFace is not None,
            "configured": bool(self._client),
            "host": self.host,
        }

    def get_dashboard(self, uid: str) -> Dict[str, Any]:
        """Fetch dashboard metadata by UID.

        Returns structured error dict if unavailable instead of raising.
        """
        if not GrafanaFace:
            return {"error": "grafana_api_not_installed"}
        if not self._client:
            return {"error": "grafana_not_configured", "host": self.host}
        try:
            data = self._client.dashboard.get_dashboard(uid)
            return {"dashboard": data}
        except Exception as exc:  # pragma: no cover - network/API issues
            return {"error": "grafana_request_failed", "detail": str(exc)}

    def health(self) -> Dict[str, Any]:
        """Attempt a lightweight org listing as a pseudo health check."""
        if not GrafanaFace:
            return {"status": "unavailable", "reason": "grafana_api_not_installed"}
        if not self._client:
            return {"status": "unconfigured", "host": self.host}
        try:
            orgs = self._client.organizations.get_organizations()
            return {"status": "ok", "org_count": len(orgs)}
        except Exception as exc:  # pragma: no cover
            return {"status": "error", "detail": str(exc)}


def probe_optional_libs() -> Dict[str, bool]:
    """Detect presence of optional heavy dependencies.

    Uses importlib to avoid importing modules that might have side effects.
    """
    import importlib
    from importlib import util

    libs = [
        ("numpy", "numpy"),
        ("pandas", "pandas"),
        ("sklearn", "scikit-learn"),
        ("torch", "torch"),
        ("tensorflow", "tensorflow"),
        ("xgboost", "xgboost"),
        ("lightgbm", "lightgbm"),
        ("stable_baselines3", "stable-baselines3"),
        ("gym", "gym"),
        ("aiohttp", "aiohttp"),
        ("asyncpg", "asyncpg"),
        ("aioredis", "aioredis"),
        ("mlflow", "mlflow"),
    ]
    availability: Dict[str, bool] = {}
    for mod_name, label in libs:
        try:
            spec = util.find_spec(mod_name)
            availability[label] = spec is not None
        except Exception:
            availability[label] = False
    return availability
