@echo off
echo 🔧 CONFIGURACION RAPIDA APIs NEXT.JS
echo ====================================

cd /d "%~dp0"
cd "..\dashboard-next"

echo 📁 Creando estructura de carpetas...
mkdir app\api\solana\price
mkdir app\api\solana\test
mkdir app\api\tbcoin\data

echo ✅ Carpetas creadas:
dir app\api /s

echo.
echo 📄 Ahora crea los archivos route.ts manualmente:
echo 1. app/api/solana/price/route.ts
echo 2. app/api/tbcoin/data/route.ts
echo 3. app/api/solana/test/route.ts
echo.
echo 🧪 Luego prueba con:
echo curl -X GET "http://localhost:3001/api/solana/price"
echo.
pause
