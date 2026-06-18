"""Cloud LLM client with mock mode for development.

No local LLM (Ollama, llama.cpp, etc.). When LLM_MOCK_ENABLED=true or LLM_API_KEY
is empty, returns a template-based mock grounded in retrieved context.
When LLM_API_KEY is set and LLM_MOCK_ENABLED=false, calls OpenAI-compatible API.
"""

from app.core.config import settings
from app.llm.prompts import SYSTEM_PROMPT, build_user_prompt
from app.vectorstore.base import RetrievedChunk


async def generate_hr_answer(
    question: str,
    language: str,
    chunks: list[RetrievedChunk],
) -> str:
    context = _format_context(chunks)

    if settings.llm_mock_enabled or not settings.llm_api_key:
        return _mock_answer(question, language, chunks)

    return await _call_cloud_api(question, language, context)


def _format_context(chunks: list[RetrievedChunk]) -> str:
    parts = []
    for i, c in enumerate(chunks, start=1):
        parts.append(
            f"[Source {i}]\n"
            f"Title: {c.title}\n"
            f"Page: {c.page or 'n/a'}\n"
            f"Section: {c.section or 'n/a'}\n"
            f"Text: {c.text[:800]}"
        )
    return "\n\n".join(parts)


def _mock_answer(question: str, language: str, chunks: list[RetrievedChunk]) -> str:
    """Template mock — not a local LLM. Grounded in retrieved chunk text only."""
    top = chunks[0]
    source_ref = top.title
    if top.section:
        source_ref += f" ({top.section})"

    snippets = " ".join(c.text.strip()[:200] for c in chunks[:2])

    templates = {
        "sq": (
            f"Bazuar në dokumentin «{source_ref}», ja informacioni relevant:\n\n"
            f"{snippets}\n\n"
            f"(Përgjigje mock — aktivizo LLM_API_KEY dhe vendos LLM_MOCK_ENABLED=false për përgjigje nga modeli cloud.)"
        ),
        "it": (
            f"In base al documento «{source_ref}», ecco le informazioni rilevanti:\n\n"
            f"{snippets}\n\n"
            f"(Risposta mock — imposta LLM_API_KEY e LLM_MOCK_ENABLED=false per risposte dal modello cloud.)"
        ),
        "sr": (
            f"Na osnovu dokumenta «{source_ref}», evo relevantnih informacija:\n\n"
            f"{snippets}\n\n"
            f"(Mock odgovor — postavite LLM_API_KEY i LLM_MOCK_ENABLED=false za odgovore sa cloud modela.)"
        ),
        "en": (
            f"Based on document «{source_ref}», here is the relevant information:\n\n"
            f"{snippets}\n\n"
            f"(Mock answer — set LLM_API_KEY and LLM_MOCK_ENABLED=false for cloud model responses.)"
        ),
    }
    return templates.get(language, templates["en"])


async def _call_cloud_api(question: str, language: str, context: str) -> str:
    from openai import AsyncOpenAI

    client = AsyncOpenAI(
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url or None,
    )
    response = await client.chat.completions.create(
        model=settings.llm_model,
        temperature=settings.llm_temperature,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(question, language, context)},
        ],
    )
    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("Cloud LLM returned empty response")
    return content
