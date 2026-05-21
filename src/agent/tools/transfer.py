from src.agent.tools.client import get, post


async def get_bank_accounts(token: str | None = None) -> list:
    result = await get("/api/v1/accounts", token=token)
    return result.get("data", [])


async def get_transfer_limit(account_id: str, token: str | None = None) -> dict:
    result = await get(f"/api/v1/accounts/{account_id}/balance", token=token)
    return result.get("data", {})


async def execute_transfer(body: dict, token: str | None = None) -> dict:
    result = await post("/api/v1/transfers", token=token, body=body)
    return result.get("data", {})


async def get_transfer_history(account_id: str, token: str | None = None) -> list:
    result = await get(f"/api/v1/accounts/{account_id}/transactions", token=token)
    return result.get("data", [])
