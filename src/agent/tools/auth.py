from src.agent.tools.client import post


async def verify_pin(pin: str, token: str | None = None) -> dict:
    result = await post("/api/v1/auth/pin/verify", token=token, body={"pin": pin})
    return result.get("data", {})
