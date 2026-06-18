from fastapi import APIRouter

from app.api.routes.health import router as health_router

ai_router = APIRouter()
ai_router.include_router(health_router, tags=["health"])
