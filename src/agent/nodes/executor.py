from src.agent.state import ChatAgentState


def executor_node(state: ChatAgentState) -> dict:
    # TODO: 백엔드 API 호출 (이체/주문/설정변경)
    return {"current_task": "executed"}
