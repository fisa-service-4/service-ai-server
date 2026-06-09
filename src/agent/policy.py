from src.agent.state import ChatAgentState

# 금융 액션(STOCK/TRANSFER/ASSET) 진입 전 순차 적용할 정책 목록
# 새 정책 추가 시 여기에만 함수 추가
FINANCIAL_POLICIES: list = []
