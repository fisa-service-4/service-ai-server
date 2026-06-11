import logging

from langgraph.types import interrupt

from src.agent.state import ChatAgentState
from src.agent.tools.auth import verify_pin
from src.agent.nodes.log_utils import log_node

logger = logging.getLogger(__name__)


@log_node("Verifier")
async def verifier_node(state: ChatAgentState) -> dict:
    # 직전 노드(Transfer_Check / Stock_Check / Asset_Action)가 추가한 확인 메시지를
    # interrupt value 로 전달 → 부모 그래프 snapshot.interrupts[0].value 로 읽을 수 있음
    ai_msgs = [m for m in state.get("messages", []) if isinstance(m, dict) and m.get("role") == "assistant"]
    confirm_msg = ai_msgs[-1]["content"] if ai_msgs else "PIN을 입력해 주세요."
    pin = interrupt(confirm_msg)

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
        _action = {"TRANSFER": "이체", "STOCK": "주문", "ASSET": "설정"}.get(intent, "요청")
        fail_msg = f"PIN이 일치하지 않습니다. {_action}을 다시 요청해 주세요."
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
