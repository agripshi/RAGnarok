#!/bin/bash
# RAGnarok — Azure Deployment Script (Linux/Ubuntu)
# Usage: bash scripts/deploy-azure.sh
# Run from repo root after: az login

set -e

RESOURCE_GROUP="${RESOURCE_GROUP:-ragnarok-hr-hub-rg}"
LOCATION="${LOCATION:-westeurope}"
APP_PREFIX="${APP_PREFIX:-ragnarok-hr-hub}"
INTERNAL_TOKEN="${INTERNAL_TOKEN:-ragnarok-internal-$RANDOM}"

API_APP="$APP_PREFIX-api"
AI_APP="$APP_PREFIX-ai"
WEB_APP="$APP_PREFIX-web"
PLAN_NAME="$APP_PREFIX-plan"

echo ""
echo "=== RAGnarok Azure Deployment ==="
echo "Resource Group : $RESOURCE_GROUP"
echo "Location       : $LOCATION"
echo "API            : https://$API_APP.azurewebsites.net"
echo "AI             : https://$AI_APP.azurewebsites.net"
echo "Frontend       : https://$WEB_APP.azurestaticapps.net"
echo ""

# ── 1. Login check ────────────────────────────────────────────────────────────
echo "[1/8] Checking Azure login..."
ACCOUNT=$(az account show 2>/dev/null) || { echo "Not logged in. Run: az login"; exit 1; }
echo "  Logged in: $(echo $ACCOUNT | python3 -c "import sys,json; a=json.load(sys.stdin); print(a['user']['name'], '|', a['name'])")"

# ── 2. Resource Group ─────────────────────────────────────────────────────────
echo ""
echo "[2/8] Creating resource group..."
az group create --name "$RESOURCE_GROUP" --location "$LOCATION" --output none
echo "  Done."

# ── 3. App Service Plan ───────────────────────────────────────────────────────
echo ""
echo "[3/8] Creating App Service Plan (B1 Linux)..."
az appservice plan create \
    --name "$PLAN_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --sku B1 \
    --is-linux \
    --output none
echo "  Done."

# ── 4. Deploy API Backend ─────────────────────────────────────────────────────
echo ""
echo "[4/8] Deploying API backend..."
az webapp create \
    --name "$API_APP" \
    --resource-group "$RESOURCE_GROUP" \
    --plan "$PLAN_NAME" \
    --runtime "PYTHON:3.12" \
    --output none

az webapp config set \
    --name "$API_APP" \
    --resource-group "$RESOURCE_GROUP" \
    --startup-file "startup.sh" \
    --output none

az webapp config appsettings set \
    --name "$API_APP" \
    --resource-group "$RESOURCE_GROUP" \
    --settings \
        APP_ENV=production \
        DATABASE_URL="sqlite:///./ragnarok_demo.db" \
        AI_BACKEND_URL="https://$AI_APP.azurewebsites.net" \
        AI_BACKEND_INTERNAL_TOKEN="$INTERNAL_TOKEN" \
        FRONTEND_ORIGINS="https://$WEB_APP.azurestaticapps.net" \
        DEV_AUTH_ENABLED=true \
        DEV_AUTH_USER_ID=demo-user-001 \
        DEV_AUTH_EMAIL=demo.user@company.com \
        AUTHORIZED_EMAILS=demo.user@company.com \
        AUTHORIZED_USER_IDS=demo-user-001 \
        TEAM_ID=demo-team-id \
        HR_PRIVATE_CHANNEL_ID=demo-hr-channel-id \
        ADMIN_EMAILS=demo.user@company.com \
        ACCESS_CACHE_TTL_SECONDS=300 \
    --output none

echo "  Packaging API..."
cd apps/api
zip -r ../../api-deploy.zip app requirements.txt startup.sh alembic alembic.ini -x "*.pyc" -x "*/__pycache__/*" -x ".venv/*"
az webapp deployment source config-zip \
    --name "$API_APP" \
    --resource-group "$RESOURCE_GROUP" \
    --src ../../api-deploy.zip \
    --output none
rm ../../api-deploy.zip
cd ../..
echo "  API deployed: https://$API_APP.azurewebsites.net"

# ── 5. Deploy AI Backend ──────────────────────────────────────────────────────
echo ""
echo "[5/8] Deploying AI backend..."
az webapp create \
    --name "$AI_APP" \
    --resource-group "$RESOURCE_GROUP" \
    --plan "$PLAN_NAME" \
    --runtime "PYTHON:3.12" \
    --output none

az webapp config set \
    --name "$AI_APP" \
    --resource-group "$RESOURCE_GROUP" \
    --startup-file "startup.sh" \
    --output none

az webapp config appsettings set \
    --name "$AI_APP" \
    --resource-group "$RESOURCE_GROUP" \
    --settings \
        APP_ENV=production \
        AI_BACKEND_INTERNAL_TOKEN="$INTERNAL_TOKEN" \
        VECTOR_DB=memory \
        LLM_MOCK_ENABLED=true \
        DEFAULT_TEAM_ID=demo-team-id \
        DEFAULT_CHANNEL_ID=demo-hr-channel-id \
        HR_DOCS_LOCAL_DIR=./data/hr-docs \
    --output none

echo "  Packaging AI (including HR docs)..."
cd apps/ai
mkdir -p data/hr-docs
cp ../../data/hr-docs/* data/hr-docs/ 2>/dev/null || true
zip -r ../../ai-deploy.zip app requirements.txt startup.sh data -x "*.pyc" -x "*/__pycache__/*" -x ".venv/*"
rm -rf data
az webapp deployment source config-zip \
    --name "$AI_APP" \
    --resource-group "$RESOURCE_GROUP" \
    --src ../../ai-deploy.zip \
    --output none
rm ../../ai-deploy.zip
cd ../..
echo "  AI deployed: https://$AI_APP.azurewebsites.net"

# ── 6. Build & Deploy Frontend ────────────────────────────────────────────────
echo ""
echo "[6/8] Building frontend..."
cd apps/web

cat > .env.production << EOF
VITE_API_BASE_URL=https://$API_APP.azurewebsites.net
VITE_ENABLE_TEAMS_AUTH=false
VITE_ENABLE_MOCK_TEAMS_SHELL=false
VITE_DEV_AUTH_TOKEN=dev-token
VITE_APP_DISPLAY_NAME=HR Hub
EOF

npm run build

echo "  Creating Static Web App..."
az staticwebapp create \
    --name "$WEB_APP" \
    --resource-group "$RESOURCE_GROUP" \
    --location "$LOCATION" \
    --output none

echo "  Deploying frontend..."
az staticwebapp deploy \
    --name "$WEB_APP" \
    --resource-group "$RESOURCE_GROUP" \
    --source dist \
    --output none

rm -f .env.production
cd ../..
echo "  Frontend deployed: https://$WEB_APP.azurestaticapps.net"

# ── 7. Update Teams Manifest ──────────────────────────────────────────────────
echo ""
echo "[7/8] Updating Teams manifest..."
python3 - << PYEOF
import json

with open("apps/web/appPackage/manifest.json") as f:
    m = json.load(f)

m["staticTabs"][0]["contentUrl"] = "https://$WEB_APP.azurestaticapps.net"
m["staticTabs"][0]["websiteUrl"] = "https://$WEB_APP.azurestaticapps.net"
m["validDomains"] = [
    "$WEB_APP.azurestaticapps.net",
    "$API_APP.azurewebsites.net"
]

with open("apps/web/appPackage/manifest.json", "w") as f:
    json.dump(m, f, indent=2)

print("  Manifest updated.")
PYEOF

cd apps/web/appPackage
zip -j ../ragnarok-teams-azure.zip manifest.json color.png outline.png
cd ../../..
echo "  Teams zip ready: apps/web/ragnarok-teams-azure.zip"

# ── 8. Health check ───────────────────────────────────────────────────────────
echo ""
echo "[8/8] Waiting for services to start (30s)..."
sleep 30

API_STATUS=$(curl -sf "https://$API_APP.azurewebsites.net/api/health" 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','?'))" 2>/dev/null || echo "starting...")
AI_STATUS=$(curl -sf  "https://$AI_APP.azurewebsites.net/ai/health"  2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','?'))" 2>/dev/null || echo "starting...")

echo "  API health : $API_STATUS"
echo "  AI  health : $AI_STATUS"

echo ""
echo "=== DONE ==="
echo "Upload apps/web/ragnarok-teams-azure.zip to Teams."
echo "Internal token (save this): $INTERNAL_TOKEN"
