# Start HR Hub locally (Windows PowerShell) ÔÇö interactive dev windows
# Usage: .\scripts\start-dev.ps1

$root = Split-Path -Parent $PSScriptRoot

Write-Host "Starting HR Hub (interactive dev mode)..." -ForegroundColor Cyan

# Free ports from stale dev servers
foreach ($port in 8000, 8001, 5173) {
  Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue |
    Select-Object -ExpandProperty OwningProcess -Unique |
    ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }
}
Start-Sleep -Seconds 2

# AI Backend
Start-Process powershell -ArgumentList @(
  "-NoExit", "-Command",
  "cd '$root\apps\ai'; .\.venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8001 --reload"
)

Start-Sleep -Seconds 3

# Backend API
Start-Process powershell -ArgumentList @(
  "-NoExit", "-Command",
  "cd '$root\apps\api'; .\.venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000 --reload"
)

Start-Sleep -Seconds 2

# Frontend
Start-Process powershell -ArgumentList @(
  "-NoExit", "-Command",
  "cd '$root\apps\web'; npm run dev -- --host 127.0.0.1 --port 5173"
)

Write-Host ""
Write-Host "Services starting:" -ForegroundColor Green
Write-Host "  AI:       http://127.0.0.1:8001/ai/health"
Write-Host "  Backend:  http://127.0.0.1:8000/api/health"
Write-Host "  Frontend: http://127.0.0.1:5173  (edit apps/web/src - saves hot-reload)"
Write-Host ""
Write-Host "Wait ~10s for AI auto-ingest, then open the frontend." -ForegroundColor Yellow
