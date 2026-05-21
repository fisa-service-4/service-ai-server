from src.agent.state import ChatAgentState


def verifier_node(state: ChatAgentState) -> dict:
    # graph.py에서 interrupt_before=["Verifier"]로 설정되어 있음
    # 이 노드 실행 전 그래프가 중단되고 PIN 입력 대기
    # 재개 시 외부에서 pin_verified 값 주입
    return {}
