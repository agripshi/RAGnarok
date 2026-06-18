from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.errors import AppError
from app.core.exception_handlers import app_error_handler, unhandled_error_handler
from app.db.init_db import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="RAGnarok Backend API", version="0.3.0", lifespan=lifespan)

_cors_origins = (
    ["*"]
    if settings.app_env == "local"
    else settings.frontend_origin_list
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=settings.app_env != "local",
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(Exception, unhandled_error_handler)
app.include_router(api_router, prefix="/api")
