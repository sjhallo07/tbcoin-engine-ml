Write-Host "🔧 CONFIGURACION RAPIDA APIs NEXT.JS"
Write-Host "===================================="

Set-Location -Path (Split-Path -Parent $MyInvocation.MyCommand.Definition)
Set-Location -Path ..\dashboard-next -ErrorAction SilentlyContinue

Write-Host "📁 Creando estructura de carpetas..."
New-Item -ItemType Directory -Force -Path "app/api/solana/price" | Out-Null
New-Item -ItemType Directory -Force -Path "app/api/solana/test" | Out-Null
New-Item -ItemType Directory -Force -Path "app/api/tbcoin/data" | Out-Null

Write-Host "✅ Carpetas creadas:"
Get-ChildItem -Path app/api -Recurse | Format-Table -AutoSize

Write-Host ""
Write-Host "📄 Ahora crea los archivos route.ts manualmente:"
Write-Host "1. app/api/solana/price/route.ts"
Write-Host "2. app/api/tbcoin/data/route.ts"
Write-Host "3. app/api/solana/test/route.ts"
Write-Host ""
Write-Host "🧪 Luego prueba con:"
Write-Host "Invoke-RestMethod -Uri \"http://localhost:3001/api/solana/price\" -Method GET"

Write-Host ""
Pause
