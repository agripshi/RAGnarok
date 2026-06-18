#!/bin/bash
# Azure App Service startup — API backend
pip install -r requirements.txt --quiet
python -m alembic upgrade head 2>/dev/null || true
uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
