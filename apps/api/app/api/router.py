from fastapi import APIRouter

from app.api.routes.health import router as health_router
from app.api.routes.chat import router as chat_router
from app.api.routes.me import router as me_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(me_router, tags=["me"])
api_router.include_router(chat_router, tags=["chat"])
