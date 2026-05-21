from src.agent.state import ChatAgentState


def rag_consult_node(state: ChatAgentState) -> dict:
    # TODO: Vector DB 검색 + LLM 금융 상담
    return {"rag_context": "", "current_task": "rag_consult"}
