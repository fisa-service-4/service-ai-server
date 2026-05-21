from src.agent.state import ChatAgentState


def verifier_node(state: ChatAgentState) -> dict:
    # interrupt_before=["Verifier"] 로 PIN 입력 전 대기
    # 재개 시 외부에서 pin_verified 값을 주입받음
    return {}
