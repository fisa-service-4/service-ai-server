import uuid

from src.agent.tools.client import post


async def set_distribution(body: dict, token: str | None = None) -> dict:
    result = await post(
        "/api/v1/distributions/settings",
        token=token,
        body=body,
        extra_headers={"Idempotency-Key": str(uuid.uuid4())},
    )
    return result.get("data", {})
