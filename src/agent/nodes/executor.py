from src.agent.state import ChatAgentState
from src.agent.tools.stock import execute_buy_order, execute_sell_order
from src.agent.tools.transfer import execute_transfer
from src.agent.tools.asset import update_salary_setting


async def executor_node(state: ChatAgentState) -> dict:
    intent = state.get("intent")
    pending_action = state.get("pending_action", {})
    token = state.get("token")

    try:
        if intent == "STOCK":
            stock_info = state.get("stock_info", {})
            account_id = stock_info.get("account_id")
            if stock_info.get("order_type") == "BUY":
                result = await execute_buy_order(stock_info, account_id=account_id, token=token)
            else:
                result = await execute_sell_order(stock_info, account_id=account_id, token=token)

        elif intent == "TRANSFER":
            result = await execute_transfer({
                "fromAccountId": state.get("from_account_id"),
                "toAccountId": state.get("to_account_id"),
                "amount": state.get("amount"),
                "description": state.get("description"),
            }, token=token)

        elif intent == "ASSET" and pending_action.get("type") == "VIRTUAL_SALARY":
            result = await update_salary_setting({
                "targetSalary": pending_action.get("targetSalary"),
                "investmentAmount": pending_action.get("investmentAmount"),
                "emergencyAmount": pending_action.get("emergencyAmount"),
            }, token=token)

        else:
            result = {}

        if intent == "ASSET" and pending_action.get("type") == "VIRTUAL_SALARY":
            salary = pending_action.get("targetSalary") or 0
            investment = pending_action.get("investmentAmount") or 0
            emergency = pending_action.get("emergencyAmount") or 0
            message = (
                f"가상월급 설정이 적용되었습니다.\n"
                f"• 가상월급: {salary:,}원\n"
                f"• 투자 이체액: {investment:,}원\n"
                f"• 비상금 이체액: {emergency:,}원"
            )
        else:
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
