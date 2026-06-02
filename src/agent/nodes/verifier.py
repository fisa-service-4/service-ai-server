import logging

from langgraph.types import interrupt

from src.agent.state import ChatAgentState
from src.agent.tools.auth import verify_pin

logger = logging.getLogger(__name__)


async def verifier_node(state: ChatAgentState) -> dict:
    # interrupt() 호출 → 그래프 일시정지, resume 시 입력값 반환
    pin = interrupt("PIN을 입력해 주세요.")

    logger.info("[Verifier] interrupt resume 값: type=%s repr=%s", type(pin).__name__, repr(pin))
    pin_str = str(pin).strip() if pin else ""
    logger.info("[Verifier] pin_str=%s", pin_str)
    token = state.get("token")
    intent = state.get("intent")

    try:
        result = await verify_pin(pin_str, token=token)
        matched = result.get("matched", False)
        logger.info("[Verifier] PIN 검증 결과: result=%s, matched=%s", result, matched)
    except Exception as e:
        logger.error("[Verifier] PIN 검증 오류: %s", e)
        matched = False
        result = {}

    if not matched:
        fail_msg = "PIN이 일치하지 않습니다. 주문을 다시 요청해 주세요."
        return {
            "stock_pin_verified": False,
            "transfer_pin_verified": False,
            "apply_pin_verified": False,
            "messages": state["messages"] + [{"role": "assistant", "content": fail_msg}],
        }

    if intent == "STOCK":
        return {"stock_pin_verified": True}
    elif intent == "TRANSFER":
        return {"transfer_pin_verified": True}
    elif intent == "ASSET":
        return {"apply_pin_verified": True}
    return {}
