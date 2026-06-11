import logging

from src.agent.state import ChatAgentState
from src.agent.policy import FINANCIAL_POLICIES
from src.agent.nodes.log_utils import log_node

logger = logging.getLogger(__name__)

_FINANCIAL_INTENTS = {"STOCK", "TRANSFER", "ASSET"}


@log_node("Guard")
async def guard_node(state: ChatAgentState) -> dict:
    intent = state.get("intent", "UNKNOWN")
    logger.info("[Guard] intent=%s 정책 체크 시작", intent)

    if intent not in _FINANCIAL_INTENTS:
        return {"guard_passed": True, "guard_reason": ""}

    for policy in FINANCIAL_POLICIES:
        passed, reason = await policy(state)
        if not passed:
            logger.warning("[Guard] 정책 차단: %s", reason)
            return {
                "guard_passed": False,
                "guard_reason": reason,
                "messages": state["messages"] + [{"role": "assistant", "content": reason}],
            }

    return {"guard_passed": True, "guard_reason": ""}
