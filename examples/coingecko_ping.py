"""Check CoinGecko Pro API server status using the official SDK."""

from __future__ import annotations

import os
import sys
from typing import Optional

from coingecko_sdk import APIError, Coingecko, RateLimitError


def _build_client() -> tuple[Coingecko, str]:
    """Configure the SDK client, preferring Pro keys when available."""

    pro_key = os.environ.get("COINGECKO_PRO_API_KEY")
    demo_key = os.environ.get("COINGECKO_DEMO_API_KEY")
    environment = "pro" if pro_key else "demo"

    if environment == "demo" and not demo_key:
        raise RuntimeError(
            "COINGECKO_DEMO_API_KEY is required when no Pro API key is configured."
        )

    client = Coingecko(
        pro_api_key=pro_key,
        demo_api_key=demo_key,
        environment=environment,
        max_retries=3,
    )
    return client, environment


def ping() -> Optional[str]:
    """Ping the CoinGecko API and return the server message when available."""
    client, _ = _build_client()
    response = client.ping.get()
    # The SDK returns a pydantic model; support both attribute and dict-like access just in case.
    if hasattr(response, "gecko_says"):
        return response.gecko_says
    if isinstance(response, dict):  # pragma: no cover - safety branch
        return response.get("gecko_says")
    return None


def main() -> None:
    try:
        client, environment = _build_client()
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(2)

    try:
        response = client.ping.get()
        if hasattr(response, "gecko_says"):
            gecko_says = response.gecko_says
        elif isinstance(response, dict):  # pragma: no cover - safety branch
            gecko_says = response.get("gecko_says")
        else:  # pragma: no cover - defensive
            gecko_says = None
    except RateLimitError as exc:
        print("Rate limit exceeded. Please retry later.", file=sys.stderr)
        if exc.status:
            print(f"Status code: {exc.status}", file=sys.stderr)
        sys.exit(1)
    except APIError as exc:
        print(f"API error: {exc}", file=sys.stderr)
        sys.exit(1)
    else:
        message = gecko_says or "No status message returned."
        print(f"Environment: {environment}")
        print(f"CoinGecko server response: {message}")


if __name__ == "__main__":
    main()
