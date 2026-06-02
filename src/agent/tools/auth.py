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
        logger.info("[Auth] PIN verify status=%s body=%s", response.status_code, response.text[:200])
        try:
            body = response.json()
            data = body.get("data", {})
            logger.info("[Auth] PIN verify data=%s", data)
            # success:true인데 data에 matched가 없으면 → 백엔드가 성공으로 간주
            if body.get("success") and "matched" not in data:
                return {"matched": True, "pinToken": data.get("pinToken", "")}
            return data
        except Exception as ex:
            logger.error("[Auth] PIN verify JSON 파싱 실패: %s", ex)
            return {"matched": False}
