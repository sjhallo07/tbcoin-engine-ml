<#
    Setup Python 3.11 virtual environment and install full requirements.

    Usage (PowerShell):
        pwsh -File .\scripts\setup_python311.ps1

    Or from repo root (if execution policy permits):
        .\scripts\setup_python311.ps1

    This script:
      1. Detects a py.exe launcher with 3.11.
      2. Creates .venv_3_11 (non-conflicting with existing .venv).
      3. Upgrades pip.
      4. Installs all requirements (including guarded ML/RL libs).
      5. Prints import verification summary.
#>

Param(
    [string]$VenvName = ".venv_3_11",
    [switch]$Force
)

function Fail($msg) { Write-Error $msg; exit 1 }

Write-Host "[setup] Checking for Python 3.11..." -ForegroundColor Cyan
$python311 = & py -3.11 -c "import sys; print(sys.executable)" 2>$null
if (-not $python311) { Fail "Python 3.11 not found via py launcher. Install from python.org and retry." }
Write-Host "[setup] Using interpreter: $python311" -ForegroundColor Green

if (Test-Path $VenvName) {
    if ($Force) {
        Write-Host "[setup] Removing existing venv $VenvName (force)." -ForegroundColor Yellow
        Remove-Item -Recurse -Force $VenvName
    } else {
        Write-Host "[setup] Existing venv $VenvName found. Skipping creation." -ForegroundColor Yellow
    }
}

if (-not (Test-Path $VenvName)) {
    Write-Host "[setup] Creating virtual environment $VenvName" -ForegroundColor Cyan
    & py -3.11 -m venv $VenvName || Fail "venv creation failed"
}

$venvPython = Join-Path $VenvName "Scripts/python.exe"
Write-Host "[setup] Upgrading pip" -ForegroundColor Cyan
& $venvPython -m pip install --upgrade pip || Fail "pip upgrade failed"

Write-Host "[setup] Installing requirements (full stack)" -ForegroundColor Cyan
& $venvPython -m pip install -r requirements.txt || Fail "requirements install failed"

Write-Host "[verify] Importing key libraries" -ForegroundColor Cyan
$code = @'
import importlib, json
mods = ["fastapi","uvicorn","numpy","pandas","sklearn","torch","tensorflow","xgboost","lightgbm","aiohttp","asyncpg","aioredis","mlflow"]
result = {}
for m in mods:
    try:
        spec = importlib.util.find_spec(m)
        result[m] = bool(spec)
    except Exception:
        result[m] = False
print(json.dumps(result))
'@
& $venvPython -c $code | Write-Host

Write-Host "[done] Activate with: `".\$VenvName\Scripts\Activate.ps1`"" -ForegroundColor Green
Write-Host "[done] Then run: `"python run_api.py`"" -ForegroundColor Green