# Start RAGnarok locally (Windows PowerShell)
# Usage: .\scripts\start-dev.ps1

$root = Split-Path -Parent $PSScriptRoot

Write-Host "Starting RAGnarok HR Assistant..." -ForegroundColor Cyan

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
  "cd '$root\apps\web'; npm run dev"
)

Write-Host ""
Write-Host "Services starting:" -ForegroundColor Green
Write-Host "  AI:       http://127.0.0.1:8001/ai/health"
Write-Host "  Backend:  http://127.0.0.1:8000/api/health"
Write-Host "  Frontend: http://localhost:5173"
Write-Host ""
Write-Host "Wait ~10s for AI auto-ingest, then open the frontend." -ForegroundColor Yellow
