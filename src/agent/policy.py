import logging

from src.agent.state import ChatAgentState

logger = logging.getLogger(__name__)


async def check_transfer_limit(state: ChatAgentState) -> tuple[bool, str]:
    """이체 한도 정책 확인"""
    # TODO: 이체 한도 API 연동 후 구현
    return True, ""


# 금융 액션(STOCK/TRANSFER/ASSET) 진입 전 순차 적용할 정책 목록
# 새 정책 추가 시 여기에만 함수 추가
FINANCIAL_POLICIES = [
    check_transfer_limit,
]
