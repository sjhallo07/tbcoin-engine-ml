#!/usr/bin/env python3
"""Quick start script to set up and run TB Coin Engine ML.

Bootstraps the environment, starts the API server, and prints a live
CoinGecko market snapshot so operators can verify external connectivity.
"""
import os
import sys
import subprocess

from typing import Dict, Iterable, Optional

from coingecko_sdk import APIError, Coingecko, RateLimitError


def check_python_version():
    """Check if Python version is 3.11+"""
    if sys.version_info < (3, 11):
        print("❌ Python 3.11 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version_info.major}.{sys.version_info.minor}")
    return True


def create_env_file():
    """Create .env file if it doesn't exist"""
    if not os.path.exists('.env'):
        print("📝 Creating .env file...")
        if os.path.exists('.env.example'):
            subprocess.run(['cp', '.env.example', '.env'])
            print("✅ Created .env from .env.example")
            print("⚠️  Please edit .env and add your OPENAI_API_KEY if you want to use LLM features")
        else:
            print("⚠️  .env.example not found")
    else:
        print("✅ .env file already exists")


def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False


def _init_coingecko_client() -> Optional[Coingecko]:
    """Initialise the CoinGecko SDK client using demo/pro keys.

    Returns a client instance when a demo key is available; otherwise, logs a
    warning and returns ``None`` so the quick start can continue without
    live market data.
    """

    demo_key = os.environ.get("COINGECKO_DEMO_API_KEY")
    pro_key = os.environ.get("COINGECKO_PRO_API_KEY")

    if not demo_key and not pro_key:
        print("⚠️  Skipping CoinGecko check (set COINGECKO_DEMO_API_KEY to enable live data suggestions).")
        return None

    client = Coingecko(
        demo_api_key=demo_key,
        pro_api_key=pro_key,
        environment="demo" if demo_key and not pro_key else "pro",
        max_retries=3,
    )
    return client


def _format_price_table(prices: Dict[str, Dict[str, float]]) -> str:
    """Format a price table showing USD quotes with simple alignment."""

    lines = ["    • {:10s} ${:>12,.2f}".format(asset.capitalize(), data.get("usd", 0.0)) for asset, data in prices.items()]
    return "\n".join(lines)


def _summarise_trending(trending_payload: Dict[str, Iterable[Dict]]) -> str:
    coins = trending_payload.get("coins") or []
    if not coins:
        return "    (No trending coins returned.)"

    rows = []
    for entry in coins[:5]:  # Limit to top 5 for readability
        item = entry.get("item", {}) if isinstance(entry, dict) else {}
        name = item.get("name", "Unknown")
        symbol = item.get("symbol", "?")
        rank = item.get("market_cap_rank")
        score = item.get("score")
        rows.append(f"    • {name} ({symbol})  rank #{rank or '—'}  score {score if score is not None else '—'}")
    return "\n".join(rows)


def show_live_market_snapshot():
    """Fetch a live CoinGecko snapshot to confirm external connectivity."""

    client = _init_coingecko_client()
    if not client:
        return

    print("\n🌐 Fetching live market snapshot from CoinGecko…")
    try:
        ping_resp = client.ping.get()
        message = getattr(ping_resp, "gecko_says", None) if ping_resp else None
        print(f"   ↳ Server status: {message or '(no message)'}")

        price_resp = client.simple.price.get(
            ids="bitcoin,ethereum,solana",
            vs_currencies="usd",
        )
        print("   ↳ Key prices:")
        print(_format_price_table(price_resp))

        trending_resp = client.search.trending.get()
        print("   ↳ Trending today:")
        print(_summarise_trending(trending_resp))

    except RateLimitError as exc:
        print("⚠️  CoinGecko rate limit reached. Try again later.")
        if exc.status:
            print(f"   Details: status {exc.status}")
    except APIError as exc:
        print(f"⚠️  CoinGecko API error: {exc}")
    except Exception as exc:  # pragma: no cover - defensive
        print(f"⚠️  Unexpected error fetching CoinGecko data: {exc}")


def run_server():
    """Run the FastAPI server"""
    print("\n🚀 Starting TB Coin Engine ML server...")
    print("📚 API Documentation will be available at: http://localhost:8000/docs")
    print("🔍 Press Ctrl+C to stop the server\n")
    
    try:
        subprocess.run([sys.executable, 'main.py'])
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped")


def main():
    """Main setup and run function"""
    print("=" * 60)
    print("TB Coin Engine ML - Quick Start")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create .env file
    create_env_file()
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Show live market snapshot (optional for demos)
    show_live_market_snapshot()

    # Run server
    run_server()


if __name__ == "__main__":
    main()
