# RAGnarok — Azure Deployment Script
# Run from the repo root on Windows: .\scripts\deploy-azure.ps1
# Prerequisites: az CLI installed, logged in via: az login

param(
    [string]$ResourceGroup  = "ragnarok-hr-hub-rg",
    [string]$Location       = "westeurope",
    [string]$AppPrefix      = "ragnarok-hr-hub",
    [string]$InternalToken  = "ragnarok-internal-$(Get-Random -Maximum 99999)"
)

$ErrorActionPreference = "Stop"

$ApiAppName = "$AppPrefix-api"
$AiAppName  = "$AppPrefix-ai"
$WebAppName = "$AppPrefix-web"
$PlanName   = "$AppPrefix-plan"

Write-Host "`n=== RAGnarok Azure Deployment ===" -ForegroundColor Cyan
Write-Host "Resource Group : $ResourceGroup"
Write-Host "Location       : $Location"
Write-Host "API App        : $ApiAppName.azurewebsites.net"
Write-Host "AI App         : $AiAppName.azurewebsites.net"
Write-Host "Frontend       : $WebAppName.azurestaticapps.net`n"

# ── 1. Login check ────────────────────────────────────────────────────────────
Write-Host "[1/8] Checking Azure login..." -ForegroundColor Yellow
$account = az account show 2>$null | ConvertFrom-Json
if (-not $account) {
    Write-Host "Not logged in. Running az login..." -ForegroundColor Yellow
    az login
    $account = az account show | ConvertFrom-Json
}
Write-Host "  Logged in as: $($account.user.name) | Subscription: $($account.name)" -ForegroundColor Green

# ── 2. Resource Group ─────────────────────────────────────────────────────────
Write-Host "`n[2/8] Creating resource group..." -ForegroundColor Yellow
az group create --name $ResourceGroup --location $Location --output none
Write-Host "  Done." -ForegroundColor Green

# ── 3. App Service Plan (B1 Linux) ────────────────────────────────────────────
Write-Host "`n[3/8] Creating App Service Plan (B1 Linux)..." -ForegroundColor Yellow
az appservice plan create `
    --name $PlanName `
    --resource-group $ResourceGroup `
    --sku B1 `
    --is-linux `
    --output none
Write-Host "  Done." -ForegroundColor Green

# ── 4. Deploy API Backend ─────────────────────────────────────────────────────
Write-Host "`n[4/8] Deploying API backend..." -ForegroundColor Yellow

az webapp create `
    --name $ApiAppName `
    --resource-group $ResourceGroup `
    --plan $PlanName `
    --runtime "PYTHON:3.12" `
    --output none

# Set startup command
az webapp config set `
    --name $ApiAppName `
    --resource-group $ResourceGroup `
    --startup-file "startup.sh" `
    --output none

# App settings
az webapp config appsettings set `
    --name $ApiAppName `
    --resource-group $ResourceGroup `
    --settings `
        APP_ENV=production `
        DATABASE_URL="sqlite:///./ragnarok_demo.db" `
        AI_BACKEND_URL="https://$AiAppName.azurewebsites.net" `
        AI_BACKEND_INTERNAL_TOKEN="$InternalToken" `
        FRONTEND_ORIGINS="https://$WebAppName.azurestaticapps.net" `
        DEV_AUTH_ENABLED=true `
        DEV_AUTH_USER_ID=demo-user-001 `
        DEV_AUTH_EMAIL=demo.user@company.com `
        AUTHORIZED_EMAILS=demo.user@company.com `
        AUTHORIZED_USER_IDS=demo-user-001 `
        TEAM_ID=demo-team-id `
        HR_PRIVATE_CHANNEL_ID=demo-hr-channel-id `
        ADMIN_EMAILS=demo.user@company.com `
        ACCESS_CACHE_TTL_SECONDS=300 `
    --output none

# Zip and deploy
Write-Host "  Packaging API..." -ForegroundColor Gray
Push-Location apps/api
Compress-Archive -Path app, requirements.txt, startup.sh, alembic, alembic.ini -DestinationPath ..\..\api-deploy.zip -Force
az webapp deployment source config-zip `
    --name $ApiAppName `
    --resource-group $ResourceGroup `
    --src ..\..\api-deploy.zip `
    --output none
Remove-Item ..\..\api-deploy.zip
Pop-Location
Write-Host "  API deployed: https://$ApiAppName.azurewebsites.net" -ForegroundColor Green

# ── 5. Deploy AI Backend ──────────────────────────────────────────────────────
Write-Host "`n[5/8] Deploying AI backend..." -ForegroundColor Yellow

az webapp create `
    --name $AiAppName `
    --resource-group $ResourceGroup `
    --plan $PlanName `
    --runtime "PYTHON:3.12" `
    --output none

az webapp config set `
    --name $AiAppName `
    --resource-group $ResourceGroup `
    --startup-file "startup.sh" `
    --output none

az webapp config appsettings set `
    --name $AiAppName `
    --resource-group $ResourceGroup `
    --settings `
        APP_ENV=production `
        AI_BACKEND_INTERNAL_TOKEN="$InternalToken" `
        VECTOR_DB=memory `
        LLM_MOCK_ENABLED=true `
        DEFAULT_TEAM_ID=demo-team-id `
        DEFAULT_CHANNEL_ID=demo-hr-channel-id `
        HR_DOCS_LOCAL_DIR=./data/hr-docs `
    --output none

Write-Host "  Packaging AI..." -ForegroundColor Gray
Push-Location apps/ai
# Include HR docs for auto-ingest on startup
$hrDocsSource = "..\..\data\hr-docs"
if (Test-Path $hrDocsSource) {
    New-Item -ItemType Directory -Force -Path "data\hr-docs" | Out-Null
    Copy-Item "$hrDocsSource\*" "data\hr-docs\" -Force
    Compress-Archive -Path app, requirements.txt, startup.sh, data -DestinationPath ..\..\ai-deploy.zip -Force
    Remove-Item data -Recurse -Force
} else {
    Compress-Archive -Path app, requirements.txt, startup.sh -DestinationPath ..\..\ai-deploy.zip -Force
}
az webapp deployment source config-zip `
    --name $AiAppName `
    --resource-group $ResourceGroup `
    --src ..\..\ai-deploy.zip `
    --output none
Remove-Item ..\..\ai-deploy.zip
Pop-Location
Write-Host "  AI deployed: https://$AiAppName.azurewebsites.net" -ForegroundColor Green

# ── 6. Build & Deploy Frontend ────────────────────────────────────────────────
Write-Host "`n[6/8] Building frontend..." -ForegroundColor Yellow
Push-Location apps/web

# Write production env
@"
VITE_API_BASE_URL=https://$ApiAppName.azurewebsites.net
VITE_ENABLE_TEAMS_AUTH=false
VITE_ENABLE_MOCK_TEAMS_SHELL=false
VITE_DEV_AUTH_TOKEN=dev-token
VITE_APP_DISPLAY_NAME=HR Hub
"@ | Set-Content .env.production

npm run build

# Create Static Web App
az staticwebapp create `
    --name $WebAppName `
    --resource-group $ResourceGroup `
    --location $Location `
    --output none

# Deploy dist
az staticwebapp deploy `
    --name $WebAppName `
    --resource-group $ResourceGroup `
    --source dist `
    --output none

Remove-Item .env.production
Pop-Location
Write-Host "  Frontend deployed: https://$WebAppName.azurestaticapps.net" -ForegroundColor Green

# ── 7. Update Teams Manifest ──────────────────────────────────────────────────
Write-Host "`n[7/8] Updating Teams manifest..." -ForegroundColor Yellow
$manifest = Get-Content apps/web/appPackage/manifest.json | ConvertFrom-Json
$manifest.staticTabs[0].contentUrl = "https://$WebAppName.azurestaticapps.net"
$manifest.staticTabs[0].websiteUrl = "https://$WebAppName.azurestaticapps.net"
$manifest.validDomains = @("$WebAppName.azurestaticapps.net", "$ApiAppName.azurewebsites.net")
$manifest | ConvertTo-Json -Depth 10 | Set-Content apps/web/appPackage/manifest.json

# Rebuild zip
Push-Location apps/web/appPackage
Compress-Archive -Path manifest.json, color.png, outline.png -DestinationPath ..\ragnarok-teams-azure.zip -Force
Pop-Location
Write-Host "  Manifest updated. New zip: apps/web/ragnarok-teams-azure.zip" -ForegroundColor Green

# ── 8. Health Check ───────────────────────────────────────────────────────────
Write-Host "`n[8/8] Verifying deployments..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

$apiHealth = Invoke-RestMethod "https://$ApiAppName.azurewebsites.net/api/health" -ErrorAction SilentlyContinue
$aiHealth  = Invoke-RestMethod "https://$AiAppName.azurewebsites.net/ai/health"  -ErrorAction SilentlyContinue

Write-Host "  API health : $($apiHealth.status)" -ForegroundColor $(if ($apiHealth.status -eq "ok") {"Green"} else {"Red"})
Write-Host "  AI health  : $($aiHealth.status)"  -ForegroundColor $(if ($aiHealth.status -eq "ok")  {"Green"} else {"Red"})

Write-Host "`n=== DONE ===" -ForegroundColor Cyan
Write-Host "Upload apps/web/ragnarok-teams-azure.zip to Teams to complete the demo setup."
Write-Host "Internal token (save this): $InternalToken"
