"""CoinGecko Onchain Demo calls for Solana and Polygon tokens/pools."""

from __future__ import annotations

import argparse
import os
import sys
from typing import Any, Dict, Iterable, List

import requests

COINGECKO_PUBLIC_API = "https://api.coingecko.com/api/v3"
DEMO_API_KEY = os.getenv("COINGECKO_DEMO_API_KEY", "YOUR_DEMO_API_KEY")
SUPPORTED_NETWORKS = {"solana", "polygon-pos"}


def _headers() -> Dict[str, str]:
    return {
        "accept": "application/json",
        "x-cg-demo-api-key": DEMO_API_KEY,
    }


def _comma_separated(addresses: Iterable[str]) -> str:
    return ",".join(addr.strip() for addr in addresses if addr.strip())


def request_json(path: str, params: Dict[str, Any] | None = None) -> Dict[str, Any] | Any:
    url = f"{COINGECKO_PUBLIC_API}{path}"
    response = requests.get(url, headers=_headers(), params=params, timeout=15)
    response.raise_for_status()
    return response.json()


def _attributes(payload: Any) -> Dict[str, Any]:
    """Extract the nested `attributes` block CoinGecko uses in onchain responses."""
    if isinstance(payload, dict):
        if "attributes" in payload and isinstance(payload["attributes"], dict):
            return payload["attributes"]
        data = payload.get("data")
        if isinstance(data, dict):
            attrs = data.get("attributes")
            if isinstance(attrs, dict):
                return attrs
            return data if isinstance(data, dict) else {}
    return payload if isinstance(payload, dict) else {}


def fetch_tokens_multi(network: str, addresses: Iterable[str], include_top_pools: bool = False) -> Any:
    joined = _comma_separated(addresses)
    if not joined:
        raise ValueError("No token addresses supplied")

    params = {"include": "top_pools"} if include_top_pools else None
    return request_json(f"/onchain/networks/{network}/tokens/multi/{joined}", params=params)


def fetch_token_info(network: str, address: str) -> Dict[str, Any]:
    if not address:
        raise ValueError("Token address is required")
    return request_json(f"/onchain/networks/{network}/tokens/{address}/info")


def fetch_new_pools(network: str, page: int | None = None) -> Dict[str, Any]:
    params: Dict[str, Any] | None = {"page": page} if page else None
    return request_json(f"/onchain/networks/{network}/new_pools", params=params)


def fetch_pool_tokens_info(network: str, pool_address: str) -> Any:
    if not pool_address:
        raise ValueError("Pool address is required")
    return request_json(f"/onchain/networks/{network}/pools/{pool_address}/info")


def print_multi_tokens(payload: Any) -> None:
    entries: List[Any] = []
    if isinstance(payload, list):
        entries = payload
    elif isinstance(payload, dict):
        maybe_data = payload.get("data")
        if isinstance(maybe_data, list):
            entries = maybe_data

    for entry in entries:
        token_block = entry.get("token") if isinstance(entry, dict) else entry
        attrs = _attributes(token_block)
        name = attrs.get("name", "?")
        symbol = attrs.get("symbol", "?").upper()
        print(f"{name} ({symbol})")
        if attrs.get("address"):
            print(f"  Address: {attrs['address']}")
        if attrs.get("coingecko_coin_id"):
            print(f"  Coin ID: {attrs['coingecko_coin_id']}")
        if attrs.get("image_url"):
            print(f"  Image URL: {attrs['image_url']}")
        if attrs.get("decimals") is not None:
            print(f"  Decimals: {attrs['decimals']}")
        price = entry.get("price_usd") or entry.get("token_price_usd")
        volume = entry.get("volume_24h_usd") or entry.get("token_volume_24h_usd")
        fdv = entry.get("fdv_usd") or entry.get("fdv")
        if price is not None:
            print(f"  Price USD: {price}")
        if volume is not None:
            print(f"  Volume 24h USD: {volume}")
        if fdv is not None:
            print(f"  FDV USD: {fdv}")
        if entry.get("top_pool"):
            pool = entry["top_pool"]
            address = pool.get("address", "?")
            dex = pool.get("dex", {}).get("name", "?")
            print(f"  Top Pool: {dex} ({address})")
        print()


def print_token_info(payload: Dict[str, Any]) -> None:
    attrs = _attributes(payload)
    print(f"Name: {attrs.get('name', '?')}")
    print(f"Symbol: {attrs.get('symbol', '?')}")
    if attrs.get("address"):
        print(f"Address: {attrs['address']}")
    decimals = attrs.get("decimals")
    if decimals is not None:
        print(f"Decimals: {decimals}")
    print(f"Coin ID: {attrs.get('coingecko_coin_id') or attrs.get('coin_id', 'N/A')}")
    if attrs.get("image_url"):
        print(f"Image URL: {attrs['image_url']}")
    image = attrs.get("image")
    if isinstance(image, dict):
        print("Image sizes:")
        for size, url in image.items():
            print(f"  {size}: {url}")
    websites = attrs.get("websites") or []
    if websites:
        print("Websites:")
        for site in websites:
            print(f"  {site}")
    socials = {
        key.replace("_handle", ""): attrs.get(key)
        for key in ["twitter_handle", "telegram_handle", "discord_url"]
        if attrs.get(key)
    }
    if socials:
        print("Socials:")
        for platform, handle in socials.items():
            print(f"  {platform}: {handle}")
    description = attrs.get("description")
    if description:
        snippet = description if len(description) < 240 else f"{description[:237]}..."
        print(f"Description: {snippet}")
    gt_score = attrs.get("gt_score")
    if gt_score is not None:
        print(f"GT Score: {gt_score}")
    gt_details = attrs.get("gt_score_details")
    if isinstance(gt_details, dict):
        print("GT Score details:")
        for metric, value in gt_details.items():
            print(f"  {metric}: {value}")
    holders = attrs.get("holders")
    if isinstance(holders, dict):
        print(f"Holders count: {holders.get('count', '?')}")
        distribution = holders.get("distribution_percentage") or {}
        if distribution:
            print("Distribution (%):")
            for bucket, value in distribution.items():
                print(f"  {bucket}: {value}")
        if holders.get("last_updated"):
            print(f"Holders last updated: {holders['last_updated']}")
    if attrs.get("is_honeypot") is not None:
        print(f"Honeypot flagged: {attrs['is_honeypot']}")


def print_new_pools(payload: Dict[str, Any]) -> None:
    for pool in payload.get("data", []):
        token = pool.get("token", {})
        dex = pool.get("dex", {})
        print(f"Pool: {token.get('name', '?')} ({token.get('symbol', '?').upper()})")
        print(f"  DEX: {dex.get('name', '?')} | Address: {pool.get('address', '?')}")
        print(f"  Price USD: {pool.get('price_usd', '?')}")
        print(f"  Volume 24h USD: {pool.get('volume_24h_usd', '?')}")
        for window in ["m5", "m15", "m30", "h1", "h6", "h24"]:
            change = pool.get("price_change", {}).get(window)
            if change is not None:
                print(f"  Price change {window}: {change}%")
        print()


def print_pool_tokens(payload: Any) -> None:
    data = payload.get("data") if isinstance(payload, dict) else payload
    if not isinstance(data, list):
        return
    for entry in data:
        attrs = _attributes(entry)
        name = attrs.get("name", "?")
        symbol = attrs.get("symbol", "?").upper()
        print(f"Token: {name} ({symbol})")
        if attrs.get("address"):
            print(f"  Address: {attrs['address']}")
        if attrs.get("coingecko_coin_id"):
            print(f"  Coin ID: {attrs['coingecko_coin_id']}")
        if attrs.get("image_url"):
            print(f"  Image URL: {attrs['image_url']}")
        if attrs.get("websites"):
            print("  Websites:")
            for site in attrs["websites"]:
                print(f"    {site}")
        holders = attrs.get("holders") or {}
        if holders.get("count"):
            print(f"  Holders: {holders['count']}")
        print()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="CoinGecko Onchain Demo API calls")
    parser.add_argument(
        "network",
        choices=sorted(SUPPORTED_NETWORKS),
        help="Target network (solana or polygon-pos)",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    multi = subparsers.add_parser("multi", help="Query multiple token addresses")
    multi.add_argument("addresses", nargs="+", help="Token contract addresses")
    multi.add_argument("--include-top-pools", action="store_true")

    info = subparsers.add_parser("info", help="Query token metadata")
    info.add_argument("address", help="Token contract address")

    pools = subparsers.add_parser("new-pools", help="List new pools in the last 48h")
    pools.add_argument("--page", type=int)

    pool_info = subparsers.add_parser("pool-info", help="Fetch metadata for pool tokens")
    pool_info.add_argument("pool_address", help="Pool contract address")

    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    try:
        if args.command == "multi":
            payload = fetch_tokens_multi(args.network, args.addresses, args.include_top_pools)
            print_multi_tokens(payload)
        elif args.command == "info":
            payload = fetch_token_info(args.network, args.address)
            print_token_info(payload)
        elif args.command == "new-pools":
            payload = fetch_new_pools(args.network, args.page)
            print_new_pools(payload)
        elif args.command == "pool-info":
            payload = fetch_pool_tokens_info(args.network, args.pool_address)
            print_pool_tokens(payload)
        else:
            raise ValueError(f"Unknown command {args.command}")
    except requests.HTTPError as exc:  # pragma: no cover - manual demo script
        print(f"Request failed: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
