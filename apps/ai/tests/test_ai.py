import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


def _rag_payload(**overrides) -> dict:
    payload = {
        "request_id": "t",
        "user_id": "u",
        "conversation_id": "c",
        "question": "test",
        "location": "al",
        "authorization_scope": {
            "team_id": "demo-team-id",
            "channel_id": "demo-hr-channel-id",
            "allowed": True,
        },
    }
    payload.update(overrides)
    return payload


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
            json=_rag_payload(
                authorization_scope={
                    "team_id": "demo-team-id",
                    "channel_id": "demo-hr-channel-id",
                    "allowed": False,
                }
            ),
        )
    assert response.status_code == 200
    assert response.json()["status"] == "ACCESS_DENIED"


@pytest.mark.asyncio
async def test_rag_requires_location():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = _rag_payload()
        del payload["location"]
        response = await client.post(
            "/ai/rag/answer",
            headers={"Authorization": "Bearer dev-internal-token"},
            json=payload,
        )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_rag_answer_albanian():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/ai/rag/answer",
            headers={"Authorization": "Bearer dev-internal-token"},
            json=_rag_payload(
                request_id="t2",
                question="Si mund të kërkoj pushime?",
                location="al",
            ),
        )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("ANSWERED", "NOT_FOUND")
    assert data["language"] in ("sq", "en", "unknown")


@pytest.mark.asyncio
async def test_rag_requires_bearer_token():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/ai/rag/answer",
            json=_rag_payload(request_id="t3"),
        )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_routes_hidden_when_test_mode_disabled():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/ai/test/rag/answer",
            json=_rag_payload(request_id="t4"),
        )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_location_scoped_retrieval():
    from app.schemas.ingest import IngestRequest
    from app.services.ingestion_service import IngestionService

    await IngestionService().sync_documents(
        IngestRequest(
            team_id="demo-team-id",
            channel_id="demo-hr-channel-id",
            force_reindex=True,
        )
    )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        al_response = await client.post(
            "/ai/rag/answer",
            headers={"Authorization": "Bearer dev-internal-token"},
            json=_rag_payload(
                request_id="loc-al",
                question="Albania HR portal leave request",
                location="al",
            ),
        )
        sr_response = await client.post(
            "/ai/rag/answer",
            headers={"Authorization": "Bearer dev-internal-token"},
            json=_rag_payload(
                request_id="loc-sr",
                question="Serbia HR portal leave request",
                location="sr",
            ),
        )

    if al_response.json()["status"] == "ANSWERED":
        for source in al_response.json()["sources"]:
            assert source.get("location") in (None, "al")

    if sr_response.json()["status"] == "ANSWERED":
        for source in sr_response.json()["sources"]:
            assert source.get("location") in (None, "sr")

    assert al_response.status_code == 200
    assert sr_response.status_code == 200
