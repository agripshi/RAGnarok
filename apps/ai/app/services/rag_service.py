from app.core.config import settings
from app.llm.chat_model import generate_hr_answer
from app.llm.language import CLARIFICATION, NOT_FOUND, detect_language
from app.schemas.rag import RagAnswerRequest, RagAnswerResponse, SourceDto
from app.vectorstore.chroma_store import get_vector_store


class RagService:
    async def answer_question(self, request: RagAnswerRequest) -> RagAnswerResponse:
        scope = request.authorization_scope
        if not scope.allowed:
            return RagAnswerResponse(
                status="ACCESS_DENIED",
                language="unknown",
                answer="Access denied.",
                sources=[],
            )

        language = detect_language(request.question, request.response_language_hint)
        store = get_vector_store()
        chunks = store.search(
            request.question,
            scope.team_id,
            scope.channel_id,
            settings.top_k,
        )
        filtered = [c for c in chunks if c.score >= settings.similarity_threshold]
        if not filtered and chunks and settings.llm_mock_enabled:
            filtered = [chunks[0]]

        if not filtered:
            return RagAnswerResponse(
                status="NOT_FOUND",
                language=language,
                answer=NOT_FOUND.get(language, NOT_FOUND["en"]),
                sources=[],
            )

        offices = {c.office for c in filtered if c.office and c.office != "unknown"}
        if len(offices) > 1 and not _mentions_office(request.question):
            return RagAnswerResponse(
                status="NEEDS_CLARIFICATION",
                language=language,
                answer=CLARIFICATION.get(language, CLARIFICATION["en"]),
                clarification_question=CLARIFICATION.get(language, CLARIFICATION["en"]),
                sources=[],
            )

        context_chunks = filtered[: settings.max_context_chunks]
        sources = [
            SourceDto(
                documentId=c.document_id,
                title=c.title,
                page=c.page,
                section=c.section,
                sourceUrl=c.source_url,
                modifiedAt=c.modified_at,
                confidence=round(c.score, 2),
            )
            for c in context_chunks
        ]

        try:
            answer = await generate_hr_answer(request.question, language, context_chunks)
        except Exception:
            return RagAnswerResponse(
                status="ERROR",
                language=language,
                answer=NOT_FOUND.get(language, NOT_FOUND["en"]),
                sources=[],
            )

        if not answer.strip():
            return RagAnswerResponse(
                status="NOT_FOUND",
                language=language,
                answer=NOT_FOUND.get(language, NOT_FOUND["en"]),
                sources=[],
            )

        return RagAnswerResponse(
            status="ANSWERED",
            language=language,
            answer=answer,
            sources=sources,
        )


def _mentions_office(question: str) -> bool:
    q = question.lower()
    return any(k in q for k in ("albania", "shqip", "serbia", "srbija", "italy", "italia"))
