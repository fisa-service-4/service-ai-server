from src.agent.state import ChatAgentState
from src.agent.llm import client, MODEL
from src.agent.tools.rag import search_rag_context

_SYSTEM_PROMPT = """당신은 프리랜서를 위한 AI 금융 어시스턴트입니다.
사용자의 자산 관리, 소비 패턴, 투자 분석, 금융 상담 질문에 친절하고 전문적으로 답변하세요.
분석 데이터가 있는 경우 해당 데이터를 기반으로 구체적인 인사이트를 제공하세요.
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
        system_content += f"\n\n[사용자 분석 데이터]\n{rag_context}"
    elif state.get("analysis_data"):
        system_content += f"\n\n[사용자 분석 데이터]\n{state['analysis_data']}"

    messages_for_llm = [{"role": "system", "content": system_content}] + state["messages"]

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages_for_llm,
        temperature=0.7,
    )

    ai_content = response.choices[0].message.content
    updated_messages = state["messages"] + [{"role": "assistant", "content": ai_content}]

    return {
        "messages": updated_messages,
        "rag_context": rag_context,
        "current_task": "rag_consult",
    }
