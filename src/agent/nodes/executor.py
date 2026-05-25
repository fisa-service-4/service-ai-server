from src.agent.state import ChatAgentState
from src.agent.tools.stock import execute_buy_order, execute_sell_order
from src.agent.tools.transfer import execute_transfer
from src.agent.tools.distribution import set_distribution


async def executor_node(state: ChatAgentState) -> dict:
    intent = state.get("intent")
    pending_action = state.get("pending_action", {})

    # TODO: token 연동 (백엔드 인증 완성 후)
    try:
        if intent == "STOCK":
            stock_info = state.get("stock_info", {})
            if stock_info.get("order_type") == "BUY":
                result = await execute_buy_order(stock_info)
            else:
                result = await execute_sell_order(stock_info)

        elif intent == "TRANSFER":
            result = await execute_transfer({
                "fromAccountId": state.get("from_account_id"),
                "toAccountId": state.get("to_account_id"),
                "amount": state.get("amount"),
                "description": state.get("description"),
            })

        elif intent == "ASSET" and pending_action.get("type") == "DISTRIBUTION":
            result = await set_distribution(pending_action)

        else:
            result = {}

        message = "실행이 완료되었습니다."
    except Exception:
        result = {}
        message = "실행 중 오류가 발생했습니다."

    updated_messages = state["messages"] + [{"role": "assistant", "content": message}]

    return {
        "messages": updated_messages,
        "current_task": "executed",
        "pending_action": {},
    }
