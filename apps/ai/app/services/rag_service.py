from app.core.config import settings
from app.core.locations import location_to_language
from app.llm.chat_model import generate_hr_answer
from app.llm.language import NOT_FOUND, detect_language
from app.retrieval.hr_retriever import retrieve_chunks
from app.schemas.rag import RagAnswerRequest, RagAnswerResponse, SourceDto


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

        language = detect_language(
            request.question,
            request.response_language_hint or location_to_language(request.location),
        )
        chunks = retrieve_chunks(
            request.question,
            scope.team_id,
            scope.channel_id,
            request.location,
            settings.top_k,
        )
        filtered = [c for c in chunks if c.score >= settings.similarity_threshold]
        if not filtered and chunks and settings.llm_mock_enabled:
            filtered = [chunks[0]]
        if not filtered and chunks:
            lang_chunks = [c for c in chunks if c.language == language]
            if lang_chunks:
                filtered = [lang_chunks[0]]

        if not filtered:
            return RagAnswerResponse(
                status="NOT_FOUND",
                language=language,
                answer=NOT_FOUND.get(language, NOT_FOUND["en"]),
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
                location=c.location,
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
