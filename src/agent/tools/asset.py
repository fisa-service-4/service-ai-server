from src.agent.tools.client import get, patch, post
from src.pipeline.db import get_analytics_pool


async def get_analysis_data(user_id: str) -> dict:
    pool = await get_analytics_pool()
    async with pool.acquire() as conn:
        pattern = await conn.fetchrow(
            "SELECT consumption_type, summary, risk_score FROM analysis_consumption_pattern WHERE user_id = $1 ORDER BY analyzed_at DESC LIMIT 1",
            int(user_id),
        )
        briefing = await conn.fetchrow(
            "SELECT briefing_summary FROM analysis_ai_briefing_history WHERE user_id = $1 ORDER BY created_at DESC LIMIT 1",
            int(user_id),
        )
    return {
        "consumption_pattern": dict(pattern) if pattern else {},
        "briefing": dict(briefing) if briefing else {},
    }


async def get_bank_balance(account_id: str, token: str | None = None) -> dict:
    result = await get(f"/api/v1/accounts/{account_id}/balance", token=token)
    return result.get("data", {})



async def get_virtual_salary_setting(token: str | None = None) -> dict:
    result = await get("/api/v1/virtual-salary", token=token)
    return result.get("data", {})


async def get_salary_recommendation(token: str | None = None) -> dict:
    result = await get("/api/v1/virtual-salary/recommendation", token=token)
    return result.get("data", {})


async def update_salary_setting(body: dict, token: str | None = None) -> dict:
    result = await patch("/api/v1/virtual-salary", token=token, body=body)
    return result.get("data", {})
