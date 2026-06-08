import logging

from src.agent.state import ChatAgentState
from src.agent.tools.stock import execute_buy_order, execute_sell_order
from src.agent.tools.transfer import execute_transfer
from src.agent.tools.asset import update_salary_setting

logger = logging.getLogger(__name__)


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
                "toBankCode": state.get("to_bank_code"),
                "toAccountNumber": state.get("to_account_number"),
                "transferAmount": state.get("amount"),
                "requestedBy": "AI",
            }, token=token)

        elif intent == "ASSET" and pending_action.get("type") == "VIRTUAL_SALARY":
            result = await update_salary_setting({
                "targetSalary": pending_action.get("targetSalary"),
                "investmentAmount": pending_action.get("investmentAmount"),
                "emergencyAmount": pending_action.get("emergencyAmount"),
            }, token=token)

        else:
            result = {}

        if intent == "STOCK":
            stock_info = state.get("stock_info", {})
            order_type = "매수" if stock_info.get("order_type") == "BUY" else "매도"
            name = stock_info.get("name", "")
            quantity = stock_info.get("quantity") or 0
            price_type = stock_info.get("price_type", "MARKET")
            if price_type == "LIMIT":
                limit_price = stock_info.get("price")
                price_str = f"지정가 {int(limit_price):,}원" if limit_price else "-"
                title = "주문 완료"
            else:
                price_str = "시장가"
                title = "주문 완료"
            message = (
                f"✅ {title}\n"
                f"• 종목: {name}\n"
                f"• 주문 유형: {order_type}\n"
                f"• 수량: {quantity:,}주\n"
                f"• 가격: {price_str}"
            )
        elif intent == "ASSET" and pending_action.get("type") == "VIRTUAL_SALARY":
            salary = pending_action.get("targetSalary") or 0
            investment = pending_action.get("investmentAmount") or 0
            emergency = pending_action.get("emergencyAmount") or 0
            message = (
                f"✅ 가상월급 설정 완료\n"
                f"• 가상월급: {salary:,}원\n"
                f"• 투자 이체액: {investment:,}원\n"
                f"• 비상금 이체액: {emergency:,}원"
            )
        elif intent == "TRANSFER":
            _bank_names = {
                "020": "우리은행", "088": "신한은행", "004": "KB국민은행", "011": "NH농협",
                "081": "하나은행", "090": "카카오뱅크", "092": "토스뱅크", "071": "우체국",
                "089": "케이뱅크", "243": "한국투자증권", "247": "NH투자증권",
            }
            transfer_amount = state.get("amount") or 0
            to_account_number = state.get("to_account_number", "")
            to_bank_code = state.get("to_bank_code", "")
            to_bank_name = _bank_names.get(to_bank_code, to_bank_code)
            message = (
                f"✅ 이체 완료\n"
                f"• 입금 계좌: {to_bank_name} {to_account_number}\n"
                f"• 이체 금액: {transfer_amount:,}원"
            )
        else:
            message = "실행이 완료되었습니다."
    except Exception as e:
        logger.error("[Executor] 실행 오류 intent=%s: %s", intent, e)
        result = {}
        message = "실행 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요."

    updated_messages = state["messages"] + [{"role": "assistant", "content": message}]

    return {
        "messages": updated_messages,
        "current_task": "executed",
        "pending_action": {},
    }
