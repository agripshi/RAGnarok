from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.services.ai_client import AiAnswerResponse
from app.schemas.chat import SourceCardDto


@pytest.mark.asyncio
async def test_chat_with_mocked_ai():
    mock_ai = AiAnswerResponse(
        status="ANSWERED",
        language="it",
        answer="Per richiedere le ferie, usa il portale HR.",
        sources=[
            SourceCardDto(title="italy-leave-policy.txt", confidence=0.9),
        ],
    )
    with patch("app.services.chat_service.call_ai_backend", new=AsyncMock(return_value=mock_ai)):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post(
                "/api/chat",
                headers={"Authorization": "Bearer dev-token"},
                json={
                    "conversationId": None,
                    "message": "Come posso richiedere le ferie?",
                    "teamsContext": {},
                },
            )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ANSWERED"
    assert data["language"] == "it"
    assert len(data["sources"]) == 1


@pytest.mark.asyncio
async def test_feedback_endpoint():
    mock_ai = AiAnswerResponse(
        status="ANSWERED",
        language="it",
        answer="Risposta di test.",
        sources=[SourceCardDto(title="policy.txt")],
    )
    with patch("app.services.chat_service.call_ai_backend", new=AsyncMock(return_value=mock_ai)):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            chat = await client.post(
                "/api/chat",
                headers={"Authorization": "Bearer dev-token"},
                json={"conversationId": None, "message": "Test?", "teamsContext": {}},
            )
            message_id = chat.json()["messageId"]
            fb = await client.post(
                "/api/feedback",
                headers={"Authorization": "Bearer dev-token"},
                json={"messageId": message_id, "rating": "helpful"},
            )
    assert fb.status_code == 200
    assert fb.json()["ok"] is True
