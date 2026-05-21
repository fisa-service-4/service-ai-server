from src.agent.tools.client import get, post


async def check_pin_status(token: str | None = None) -> dict:
    # TODO: 백엔드 인증 구현 후 연동
    result = await get("/api/v1/auth/pin/status", token=token)
    return result.get("data", {})


async def verify_pin(pin: str, token: str | None = None) -> dict:
    # TODO: 백엔드 인증 구현 후 연동
    result = await post("/api/v1/auth/pin/verify", token=token, body={"pin": pin})
    return result.get("data", {})
