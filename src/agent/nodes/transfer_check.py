from src.agent.state import ChatAgentState


def transfer_check_node(state: ChatAgentState) -> dict:
    # TODO: 잔액/한도 조회
    return {"transfer_info_complete": False}
