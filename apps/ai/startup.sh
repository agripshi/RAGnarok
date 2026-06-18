#!/bin/bash
# Azure App Service startup — AI backend
pip install -r requirements.txt --quiet
uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
