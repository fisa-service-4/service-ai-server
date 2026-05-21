from src.agent.tools.client import post


async def set_distribution(body: dict, token: str | None = None) -> dict:
    result = await post("/api/v1/distributions/settings", token=token, body=body)
    return result.get("data", {})


async def apply_distribution(body: dict, token: str | None = None) -> dict:
    result = await post("/api/v1/distributions/settings/apply", token=token, body=body)
    return result.get("data", {})
