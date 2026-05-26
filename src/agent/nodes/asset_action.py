from src.agent.state import ChatAgentState
from src.agent.llm import client, MODEL

_DISTRIBUTION_KEYWORDS = [
    "분배", "배분", "추천", "비율", "투자 비율", "저축 비율", "자산 분배",
    "자산 배분", "어떻게 나눠", "어떻게 배분", "얼마나 투자", "얼마씩",
]

_SYSTEM_PROMPT = """사용자의 자산 분석 데이터를 바탕으로 자산 분배 추천을 생성하세요.
투자 비율, 비상금 비율, 생활비 비율을 퍼센트로 추천하고 이유를 설명하세요.
한국어로 답변하세요. 답변은 3~5문장 이내로 간결하게 작성하세요."""


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

    if not any(kw in user_query for kw in _DISTRIBUTION_KEYWORDS):
        return {"pending_action": {}}

    context = f"분석 데이터: {analysis_data}\n참고 정보: {rag_context}" if rag_context else f"분석 데이터: {analysis_data}"

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": context},
        ],
        temperature=0.7,
    )

    recommendation = response.choices[0].message.content

    pending_action = {
        "type": "DISTRIBUTION",
        "recommendation": recommendation,
    }

    updated_messages = state["messages"] + [{"role": "assistant", "content": recommendation}]

    return {
        "pending_action": pending_action,
        "messages": updated_messages,
    }
