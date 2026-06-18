import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_ai_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/ai/health")
    assert response.status_code == 200
    assert response.json()["llmMode"] == "mock"


@pytest.mark.asyncio
async def test_rag_access_denied_without_scope():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/ai/rag/answer",
            headers={"Authorization": "Bearer dev-internal-token"},
            json={
                "request_id": "t",
                "user_id": "u",
                "conversation_id": "c",
                "question": "test",
                "authorization_scope": {
                    "team_id": "demo-team-id",
                    "channel_id": "demo-hr-channel-id",
                    "allowed": False,
                },
            },
        )
    assert response.status_code == 200
    assert response.json()["status"] == "ACCESS_DENIED"
