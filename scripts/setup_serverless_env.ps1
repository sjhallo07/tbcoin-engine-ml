# Creates a minimal venv for serverless (Lambda) and installs requirements-serverless.txt
param(
  [string]$Python = "py",
  [string]$VenvName = ".venv_serverless"
)

Write-Host "[serverless-setup] Creating venv: $VenvName" -ForegroundColor Cyan
& $Python -3.11 -m venv $VenvName

$activate = Join-Path $VenvName "Scripts\Activate.ps1"
if (Test-Path $activate) {
  Write-Host "[serverless-setup] Activating venv" -ForegroundColor Cyan
  . $activate
} else {
  Write-Error "Activation script not found at $activate"
  exit 1
}

python -m pip install --upgrade pip
python -m pip install -r requirements-serverless.txt

Write-Host "[serverless-setup] Installed packages:" -ForegroundColor Cyan
python -c "import sys, pkgutil; print(sys.version); print('\n'.join(sorted([p.name for p in pkgutil.iter_modules()])))"

Write-Host "[serverless-setup] Done. To activate later: .\\$VenvName\\Scripts\\Activate.ps1" -ForegroundColor Green
