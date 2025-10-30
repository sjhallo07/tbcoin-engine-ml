# Solana Starter Modules

This document describes the starter modules added to the repository:

- `solana_adapter.py` — lightweight wrapper around `solana` RPC client for basic operations.
- `ai_decision_engine.py` — minimal AI decision engine stub with placeholders for model loading and prediction.
- `executor.py` — small Flask API exposing endpoints for balance, account info, decision, and execute_decision. Includes a simple CLI to run the server locally.

Quick start
1. Create and activate a venv:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. Install minimal requirements:

```powershell
pip install -r requirements-minimal.txt
```

3. Run the executor Flask server:

```powershell
python executor.py --host 127.0.0.1 --port 5000
```

Endpoints
- GET /balance/<pubkey> — return lamports balance for a pubkey (uses devnet by default)
- GET /account/<pubkey> — return account info
- POST /decision — JSON body of feature map -> returns decision
- POST /execute_decision — simulate or execute decision depending on `AI_TRADING_ENABLED` env var

Configuration
- Use `.env.template` as a starting point and copy to `.env` to set `SOLANA_RPC_URL`, `AI_TRADING_ENABLED`, etc.

Notes and next steps
- The decision engine is a placeholder. Replace `ai_decision_engine.py` load/predict with real model code when you want to add ML dependencies.
- The Solana adapter assumes `solana` (solana-py) is available — guard production code to use KMS for signing.
- The GitHub Actions workflow `canary-model-ci.yml` is a skeleton — fill in packaging and deployment steps for your staging environment.
