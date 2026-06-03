from src.agent.state import ChatAgentState
from src.agent.llm import client, MODEL

_RECOMMEND_KEYWORDS = [
    "분배 추천", "배분 추천", "추천해줘", "추천해", "어떻게 나눠", "어떻게 배분",
    "얼마씩", "얼마나 투자", "자산 분배", "자산 배분",
]

_APPLY_KEYWORDS = [
    "적용해줘", "적용해", "설정해줘", "설정해", "그대로 해줘", "반영해줘",
]

_SYSTEM_PROMPT = """사용자의 자산 분석 데이터를 바탕으로 월 가상월급, 비상금 이체액, 투자 이체액을 금액으로 추천하세요.
비율이 아닌 구체적인 금액(원 단위)으로 추천하고 간단한 이유를 설명하세요.
한국어로 답변하세요. 답변은 3~5문장 이내로 간결하게 작성하세요.
마지막에 반드시 "적용하시겠습니까?" 라고 물어보세요."""


def asset_action_node(state: ChatAgentState) -> dict:
    analysis_data = state.get("analysis_data", {})
    intent = state.get("intent", "")
    rag_context = state.get("rag_context", "")

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

    # 적용 요청: 이전 추천이 있으면 pending_action만 set
    if is_apply:
        prev_recommendation = ""
        for msg in reversed(state["messages"]):
            if msg.get("role") == "assistant" and "적용하시겠습니까?" in msg.get("content", ""):
                prev_recommendation = msg["content"]
                break

        income = analysis_data.get("monthly_income", {}).get("total_income", 0)
        pending_action = {
            "type": "DISTRIBUTION",
            "incomeAmount": int(income),
        }
        return {"pending_action": pending_action}

    # 추천 요청: LLM으로 금액 추천 생성, pending_action 없음
    context = f"분석 데이터: {analysis_data}\n참고 정보: {rag_context}" if rag_context else f"분석 데이터: {analysis_data}"

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": context},
        ],
        temperature=0.7,
    )

    recommendation = response.choices[0].message.content or ""
    updated_messages = state["messages"] + [{"role": "assistant", "content": recommendation}]

    return {
        "pending_action": {},
        "messages": updated_messages,
    }
