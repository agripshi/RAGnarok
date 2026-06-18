from fastapi import APIRouter, HTTPException

from app.core.config import settings
from app.schemas.rag import RagAnswerRequest, RagAnswerResponse
from app.services.rag_service import RagService

router = APIRouter()
_service = RagService()


@router.post("/rag/answer", response_model=RagAnswerResponse)
async def rag_answer_test(request: RagAnswerRequest) -> RagAnswerResponse:
    if not settings.test_mode:
        raise HTTPException(status_code=404, detail="Not found")
    return await _service.answer_question(request)
