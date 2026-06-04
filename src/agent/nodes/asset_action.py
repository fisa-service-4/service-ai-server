import json

from src.agent.state import ChatAgentState
from src.pipeline.db import get_analytics_pool

_RECOMMEND_KEYWORDS = [
    "분배 추천", "배분 추천", "추천해줘", "추천해", "어떻게 나눠", "어떻게 배분",
    "얼마씩", "얼마나 투자", "자산 분배", "자산 배분",
]

_APPLY_KEYWORDS = [
    "적용해줘", "적용해", "설정해줘", "설정해", "그대로 해줘", "반영해줘",
]


async def asset_action_node(state: ChatAgentState) -> dict:
    analysis_data = state.get("analysis_data", {})
    intent = state.get("intent", "")

    if not analysis_data or intent != "ASSET":
        return {"pending_action": {}}

    user_query = ""
    for msg in reversed(state["messages"]):
        if msg.get("role") == "user":
            user_query = msg["content"]
            break

    is_apply = any(kw in user_query for kw in _APPLY_KEYWORDS)
    is_recommend = any(kw in user_query for kw in _RECOMMEND_KEYWORDS)

    if not is_recommend and not is_apply:
        return {"pending_action": {}}

    user_id = int(state.get("user_id") or 1)

    if is_apply:
        income = analysis_data.get("monthly_income", {}).get("total_income", 0)
        return {
            "pending_action": {
                "type": "DISTRIBUTION",
                "incomeAmount": int(income),
            }
        }

    # 추천 요청: DB에서 추천 데이터 조회
    try:
        pool = await get_analytics_pool()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT DISTINCT ON (recommendation_type)
                    recommendation_type, recommendation_content
                FROM analysis_ai_recommendation
                WHERE user_id = $1
                ORDER BY recommendation_type, created_at DESC
                """,
                user_id,
            )
    except Exception:
        return {"pending_action": {}}

    if not rows:
        msg = "아직 분석 데이터가 없어요. 잠시 후 다시 시도해주세요."
        return {
            "pending_action": {},
            "messages": state["messages"] + [{"role": "assistant", "content": msg}],
        }

    recs = {row["recommendation_type"]: json.loads(row["recommendation_content"]) for row in rows}

    salary = int(recs.get("SALARY", {}).get("value") or 0)
    emergency = int(recs.get("EMERGENCY", {}).get("value") or 0)
    investment = int(recs.get("INVESTMENT", {}).get("value") or 0)
    salary_summary = recs.get("SALARY", {}).get("summary", "")
    emergency_summary = recs.get("EMERGENCY", {}).get("summary", "")

    recommendation = (
        f"월 가상월급은 **{salary:,}원**, "
        f"비상금 이체액은 **{emergency:,}원**, "
        f"투자 이체액은 **{investment:,}원**으로 추천합니다.\n"
        f"{salary_summary} {emergency_summary}\n\n"
        f"적용하시겠습니까?"
    )

    return {
        "pending_action": {},
        "messages": state["messages"] + [{"role": "assistant", "content": recommendation}],
    }
