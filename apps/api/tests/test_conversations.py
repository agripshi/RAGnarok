from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.services.ai_client import AiAnswerResponse
from app.schemas.chat import SourceCardDto


@pytest.mark.asyncio
async def test_list_conversations():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/conversations", headers={"Authorization": "Bearer dev-token"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:
        assert "id" in data[0]
        assert "title" in data[0]


@pytest.mark.asyncio
async def test_conversation_history_after_chat():
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
                json={"conversationId": None, "message": "Come richiedo ferie?", "teamsContext": {}},
            )
            assert chat.status_code == 200
            conv_id = chat.json()["conversationId"]

            listed = await client.get("/api/conversations", headers={"Authorization": "Bearer dev-token"})
            assert listed.status_code == 200
            ids = [c["id"] for c in listed.json()]
            assert conv_id in ids

            detail = await client.get(
                f"/api/conversations/{conv_id}",
                headers={"Authorization": "Bearer dev-token"},
            )
            assert detail.status_code == 200
            body = detail.json()
            assert body["id"] == conv_id
            assert len(body["messages"]) == 2
            assert body["messages"][0]["role"] == "user"
            assert body["messages"][1]["role"] == "assistant"
