from src.agent.tools.client import get, post


async def get_analysis_data(user_id: str, token: str | None = None) -> dict:
    result = await get(f"/api/v1/analysis/{user_id}", token=token)
    return result.get("data", {})


async def get_bank_balance(account_id: str, token: str | None = None) -> dict:
    result = await get(f"/api/v1/accounts/{account_id}/balance", token=token)
    return result.get("data", {})


async def get_contracts(token: str | None = None) -> list:
    result = await get("/api/v1/contracts", token=token)
    return result.get("data", [])


async def get_pending_income(token: str | None = None) -> list:
    result = await get("/api/v1/contracts", token=token, params={"status": "PENDING"})
    return result.get("data", [])


async def get_virtual_salary_setting(token: str | None = None) -> dict:
    result = await get("/api/v1/virtual-salary", token=token)
    return result.get("data", {})


async def get_salary_recommendation(token: str | None = None) -> dict:
    result = await get("/api/v1/virtual-salary/recommendation", token=token)
    return result.get("data", {})


async def update_salary_setting(body: dict, token: str | None = None) -> dict:
    result = await post("/api/v1/virtual-salary", token=token, body=body)
    return result.get("data", {})
