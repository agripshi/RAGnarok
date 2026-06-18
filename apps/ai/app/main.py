from fastapi import FastAPI

from app.api.router import ai_router

app = FastAPI(title="RAGnarok AI Backend", version="0.1.0")
app.include_router(ai_router, prefix="/ai")
