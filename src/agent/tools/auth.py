import httpx
import logging

from src.agent.tools.client import _BACKEND_URL, _headers

logger = logging.getLogger(__name__)


async def verify_pin(pin: str, token: str | None = None) -> dict:
    async with httpx.AsyncClient(base_url=_BACKEND_URL, timeout=10.0) as client:
        response = await client.post(
            "/api/v1/auth/pin/verify",
            headers=_headers(token),
            json={"pin": pin},
        )
        logger.info("[Auth] PIN verify status=%s body=%s", response.status_code, response.text)
        try:
            body = response.json()
            return body.get("data", {})
        except Exception:
            return {"matched": False}
