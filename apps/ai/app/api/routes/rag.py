from fastapi import APIRouter, Depends

from app.core.security import require_internal_token
from app.schemas.rag import RagAnswerRequest, RagAnswerResponse
from app.services.rag_service import RagService

router = APIRouter()
_service = RagService()


@router.post("/rag/answer", response_model=RagAnswerResponse)
async def rag_answer(
    request: RagAnswerRequest,
    _: None = Depends(require_internal_token),
) -> RagAnswerResponse:
    return await _service.answer_question(request)
