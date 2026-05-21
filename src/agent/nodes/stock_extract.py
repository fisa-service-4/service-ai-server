from src.agent.state import ChatAgentState


def stock_extract_node(state: ChatAgentState) -> dict:
    # TODO: 종목/수량 추출 + 정보 부족 시 질문
    return {"stock_info": {}, "info_complete": False}
