import asyncio

from src.agent.state import ChatAgentState
from src.agent.llm import client, MODEL
from src.agent.tools.rag import search_rag_context

_SYSTEM_PROMPT = """당신은 프리랜서를 위한 AI 금융 어시스턴트입니다.
사용자의 자산 관리, 소비 패턴, 투자 분석, 금융 상담 질문에 친절하고 전문적으로 답변하세요.
참고 자료가 제공되는 경우 내용을 자연스럽게 녹여 답변하되, 출처 레이블([...])은 절대 응답에 노출하지 마세요.
개인 분석 데이터가 없더라도 금융 전문 지식을 바탕으로 유용한 조언을 제공하고, 추가 정보를 요구하지 마세요.
한국어로 답변하세요. 답변은 3~5문장 이내로 간결하게 작성하세요."""


async def rag_consult_node(state: ChatAgentState) -> dict:
    user_query = ""
    for msg in reversed(state["messages"]):
        if msg.get("role") == "user":
            user_query = msg["content"]
            break

    rag_context = ""
    if user_query:
        rag_context = await search_rag_context(state["user_id"], user_query)

    system_content = _SYSTEM_PROMPT
    if rag_context:
        context_text = "\n\n".join(
            chunk for chunk in (row.split("] ", 1)[-1] for row in rag_context.split("\n\n")) if chunk
        )
        system_content += f"\n\n[참고 자료]\n{context_text}"
    elif state.get("analysis_data"):
        system_content += f"\n\n[사용자 분석 데이터]\n{state['analysis_data']}"

    messages_for_llm = [{"role": "system", "content": system_content}] + state["messages"]

    try:
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model=MODEL,
            messages=messages_for_llm,
            temperature=0.7,
        )
        ai_content = response.choices[0].message.content or "죄송합니다. 응답을 생성하지 못했습니다."
    except Exception:
        ai_content = "죄송합니다. 해당 질문에는 답변하기 어렵습니다. 다른 방식으로 질문해 주시거나, 계좌 조회, 이체, 주식 주문 등 도움이 필요하신 부분을 알려주세요."

    updated_messages = state["messages"] + [{"role": "assistant", "content": ai_content}]

    return {
        "messages": updated_messages,
        "rag_context": rag_context,
        "current_task": "rag_consult",
    }
