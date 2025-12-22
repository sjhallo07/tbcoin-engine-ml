# TB Coin Engine ML — Full-Stack Quickstart

A concise path to bring up the Python backend, database, background services, and the Next.js dashboard on a fresh machine. Commands are shown for PowerShell; adjust for your shell/OS.

## Prerequisites

- Python 3.11+ and PowerShell (or bash/zsh)
- Node.js 18+ (20+ recommended) and npm
- Docker Desktop with Docker Compose
- Git configured with your remote credentials

## 1) Environment setup

```powershell
# From repo root
Copy-Item .env.example .env -ErrorAction SilentlyContinue
notepad .env   # fill TB_API_KEY, COINGECKO keys, RPC URLs, secrets
```

Key variables to review:

- `TB_API_KEY`, `SECRET_KEY`, `JWT_SECRET_KEY`
- `DATABASE_URL` (Postgres) or leave SQLite for local
- `SOLANA_RPC_URL` / EVM RPCs if you call chains
- `AI_AGENT_ENABLED`, `AI_TRADING_ENABLED` (keep trading false in dev)

## 2) Python backend

Minimal API (lighter deps):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-minimal.txt
uvicorn api_main:app --host 127.0.0.1 --port 8000
```

Full API + agents (all features):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
$env:AI_AGENT_ENABLED="true"
$env:AI_TRADING_ENABLED="false"   # stay safe in dev
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Health check:

```powershell
Invoke-RestMethod 'http://127.0.0.1:8000/health' | ConvertTo-Json -Depth 5
```

## 3) Databases and services (Docker)

Minimal data plane (Postgres + Redis):

```powershell
docker compose up -d db redis
```

Full stack (API, autonomous agent, ML worker, MLflow, MinIO, Prometheus, Grafana):

```powershell
docker compose up -d db redis mlflow minio prometheus grafana api autonomous-agent ml-worker
```

Stop stack:

```powershell
docker compose down
```

## 4) Agents (optional CLI)

Quick demo of agent orders:

```powershell
Push-Location .\agents
$py = "$(Resolve-Path ..\.venv\Scripts\python.exe)"
& $py orders.py fetch
$orders = (& $py orders.py fetch | ConvertFrom-Json).orders | ConvertTo-Json -Compress
& $py orders.py process --orders $orders
Pop-Location
```

## 5) Dashboard (Next.js)

```powershell
Push-Location .\dashboard-next
npm ci
npm run dev   # serves on http://localhost:3001
# Production build
npm run build
npm start -- -p 3001
Pop-Location
```

If Windows reports EPERM on a native module during install, close running dev servers/AV and retry `npm ci`.

## 6) Smoke checks

- API: `http://127.0.0.1:8000/health`
- Dashboard API sample: `http://127.0.0.1:3001/api/token/profile/<mint>`
- Grafana (if running): `http://localhost:3000` (user: admin / pass: admin)

## 7) Git workflow

```powershell
git status
git add tbcoin-engine-ml/docs/quickstart-fullstack.md
git commit -m "Add full-stack quickstart guide"
git push origin <your-branch>
```

> Note: Pushing requires your Git remote and credentials; not executed automatically here.

## Troubleshooting

- Missing deps: ensure the venv is activated before running `uvicorn`.
- Port conflicts: adjust `API_PORT` / `NODE_PORT` or use `-p` flags.
- Docker resource usage: stop services you don’t need with `docker compose stop <svc>`.
