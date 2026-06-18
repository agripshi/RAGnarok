import httpx

from app.core.config import settings
from app.core.errors import AiBackendError


async def trigger_ai_ingest() -> dict:
    url = f"{settings.ai_backend_url.rstrip('/')}/ai/ingest/sync"
    payload = {
        "source_mode": "local",
        "team_id": settings.team_id,
        "channel_id": settings.hr_private_channel_id,
        "force_reindex": True,
    }
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                url,
                json=payload,
                headers={"Authorization": f"Bearer {settings.ai_backend_internal_token}"},
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        raise AiBackendError(str(e)) from e
