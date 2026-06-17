import asyncio
import json

from src.agent.state import ChatAgentState
from src.agent.llm import client, MODEL
from src.pipeline.db import get_analytics_pool
from src.agent.nodes.log_utils import log_node, _insert_prompt_log, run_in_background

_CLASSIFY_PROMPT = """사용자의 자산관리 요청 의도를 분류하세요.
반드시 아래 영단어 중 하나만 출력하세요. 한국어, 설명, 다른 단어 금지.

recommend - 가상월급/분배 비율에 대한 AI 추천을 원하는 경우
            (예: 가상월급 분배 추천해줘, 분배 비율 어떻게 해야 해, 얼마씩 나눠야 해, 비상금 얼마가 적당해, 투자금 얼마로 설정할까, 월급 배분 추천해줘)
apply     - AI가 추천한 분배 설정을 실제로 적용/반영하겠다는 경우
            (예: 적용할래, 그대로 해줘, 설정해줘, 반영해줘)
consult   - 현재 자산 현황 조회, 소비 분석, 투자 성향 등 일반 상담
            (예: 이번달 지출 어때, 내 자산 알려줘, 소비 패턴 분석해줘)

출력 예시:
recommend"""


async def _classify_sub_intent(messages: list, user_id: str | None = None, session_id: int | None = None) -> str:
    user_query = ""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            user_query = msg["content"]
            break

    if not user_query:
        return "consult"

    # recommend/consult 구분이 앱 도메인 특화 개념이라 LLM이 오분류하는 패턴 보정.
    # "추천" + 분배/금융 맥락 조합은 명확하게 recommend로 처리.
    if "추천" in user_query and any(kw in user_query for kw in ["분배", "가상월급", "비상금", "투자금", "월급"]):
        return "recommend"

    try:
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model=MODEL,
            messages=[
                {"role": "system", "content": _CLASSIFY_PROMPT},
                {"role": "user", "content": user_query},
            ],
            temperature=0,
            max_tokens=10,
        )
        raw = (response.choices[0].message.content or "").strip().lower()
        run_in_background(
            _insert_prompt_log(
                user_id=user_id,
                session_id=session_id,
                prompt_type="ASSET_CLASSIFY",
                system_prompt=_CLASSIFY_PROMPT,
                user_prompt=user_query,
                ai_response=raw,
            )
        )
        if "apply" in raw or "적용" in raw or "설정" in raw or "반영" in raw:
            return "apply"
        if "recommend" in raw or "추천" in raw:
            return "recommend"
        return "consult"
    except Exception:
        return "consult"


async def _fetch_recommendations(user_id: int) -> dict | None:
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
        if not rows:
            return None
        return {row["recommendation_type"]: json.loads(row["recommendation_content"]) for row in rows}
    except Exception:
        return None


@log_node("Asset_Action")
async def asset_action_node(state: ChatAgentState) -> dict:
    if state.get("intent") not in ("ASSET", "UNKNOWN"):
        return {"pending_action": {}, "asset_action_type": "consult"}

    sub_intent = await _classify_sub_intent(
        state["messages"],
        user_id=state.get("user_id"),
        session_id=state.get("session_id"),
    )
    try:
        user_id = int(state.get("user_id") or 1)
    except ValueError:
        user_id = 1

    if sub_intent == "apply":
        recs = await _fetch_recommendations(user_id)
        if not recs:
            return {
                "pending_action": {},
                "asset_action_type": "apply",
                "messages": state["messages"] + [{"role": "assistant", "content": "아직 분석 데이터가 없어요. 잠시 후 다시 시도해 주세요."}],
            }

        salary = int((recs.get("SALARY") or {}).get("value") or 0)
        investment = int((recs.get("INVESTMENT") or {}).get("value") or 0)
        emergency = int((recs.get("EMERGENCY") or {}).get("value") or 0)
        confirm_msg = (
            f"💰 분배 설정 확인\n"
            f"• 가상월급: {salary:,}원\n"
            f"• 투자 이체액: {investment:,}원\n"
            f"• 비상금 이체액: {emergency:,}원\n"
            f"PIN을 입력해 주세요."
        )
        return {
            "pending_action": {
                "type": "VIRTUAL_SALARY",
                "targetSalary": salary,
                "investmentAmount": investment,
                "emergencyAmount": emergency,
            },
            "asset_action_type": "apply",
            "messages": state["messages"] + [{"role": "assistant", "content": confirm_msg}],
        }

    if sub_intent == "recommend":
        recs = await _fetch_recommendations(user_id)
        if not recs:
            return {
                "pending_action": {},
                "asset_action_type": "recommend",
                "messages": state["messages"] + [{"role": "assistant", "content": "아직 분석 데이터가 없어요. 잠시 후 다시 시도해 주세요."}],
            }

        salary = int((recs.get("SALARY") or {}).get("value") or 0)
        investment = int((recs.get("INVESTMENT") or {}).get("value") or 0)
        emergency = int((recs.get("EMERGENCY") or {}).get("value") or 0)
        salary_summary = (recs.get("SALARY") or {}).get("summary", "")
        emergency_summary = (recs.get("EMERGENCY") or {}).get("summary", "")

        recommendation = (
            f"💰 AI 분배 추천\n"
            f"• 가상월급: {salary:,}원\n"
            f"• 투자 이체액: {investment:,}원\n"
            f"• 비상금 이체액: {emergency:,}원\n\n"
            f"{salary_summary}\n\n"
            f"적용하시겠습니까?"
        )
        return {
            "pending_action": {},
            "asset_action_type": "recommend",
            "messages": state["messages"] + [{"role": "assistant", "content": recommendation}],
        }

    # consult — RAG_Consult 노드가 처리
    return {"pending_action": {}, "asset_action_type": "consult"}
