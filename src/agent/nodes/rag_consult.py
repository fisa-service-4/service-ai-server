from src.agent.state import ChatAgentState
from src.agent.llm import client, MODEL

_SYSTEM_PROMPT = """당신은 프리랜서를 위한 AI 금융 어시스턴트입니다.
사용자의 자산 관리, 소비 패턴, 투자 분석, 금융 상담 질문에 친절하고 전문적으로 답변하세요.
분석 데이터가 있는 경우 해당 데이터를 기반으로 구체적인 인사이트를 제공하세요.
한국어로 답변하세요."""


def rag_consult_node(state: ChatAgentState) -> dict:
    messages_for_llm = [{"role": "system", "content": _SYSTEM_PROMPT}]

    if state.get("analysis_data"):
        analysis_summary = f"\n[사용자 분석 데이터]\n{state['analysis_data']}"
        messages_for_llm[0]["content"] += analysis_summary

    messages_for_llm += state["messages"]

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages_for_llm,
        temperature=0.7,
    )

    ai_content = response.choices[0].message.content
    updated_messages = state["messages"] + [{"role": "assistant", "content": ai_content}]

    return {"messages": updated_messages, "current_task": "rag_consult"}
