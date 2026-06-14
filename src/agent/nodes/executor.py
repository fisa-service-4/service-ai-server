import asyncio
import logging

from src.agent.state import ChatAgentState
from src.agent.tools.stock import execute_buy_order, execute_sell_order
from src.agent.tools.transfer import execute_transfer
from src.agent.tools.asset import update_salary_setting
from src.agent.nodes.transfer_check import _BANK_NAMES
from src.agent.nodes.log_utils import log_node, _insert_action_log, run_in_background

logger = logging.getLogger(__name__)


def _mask_account_number(account_number: str) -> str:
    if not account_number or len(account_number) <= 4:
        return "****"
    return "****" + account_number[-4:]


def _build_action_payload(intent: str, state: ChatAgentState, pending_action: dict) -> dict:
    if intent == "STOCK":
        stock_info = state.get("stock_info", {})
        return {
            "orderType": stock_info.get("order_type"),
            "stockCode": stock_info.get("code"),
            "stockName": stock_info.get("name"),
            "quantity": stock_info.get("quantity"),
            "priceType": stock_info.get("price_type"),
        }
    if intent == "TRANSFER":
        return {
            "fromAccountId": state.get("from_account_id"),
            "toBankCode": state.get("to_bank_code"),
            "toAccountNumber": _mask_account_number(state.get("to_account_number") or ""),
            "transferAmount": state.get("amount"),
        }
    if intent == "ASSET" and pending_action.get("type") == "VIRTUAL_SALARY":
        return {
            "type": "VIRTUAL_SALARY",
            "targetSalary": pending_action.get("targetSalary"),
            "investmentAmount": pending_action.get("investmentAmount"),
            "emergencyAmount": pending_action.get("emergencyAmount"),
        }
    return {}


def _log_action(
    state: ChatAgentState,
    intent: str,
    pending_action: dict,
    executed_yn: bool,
    result_message: str,
) -> None:
    _ACTION_TYPE_MAP = {
        "TRANSFER": "TRANSFER",
        "ASSET": "AUTO_DISTRIBUTION",
    }
    if intent == "STOCK":
        stock_info = state.get("stock_info", {})
        action_type = "BUY" if stock_info.get("order_type") == "BUY" else "SELL"
    else:
        action_type = _ACTION_TYPE_MAP.get(intent, intent)

    payload = _build_action_payload(intent, state, pending_action)
    run_in_background(
        _insert_action_log(
            user_id=state.get("user_id"),
            action_type=action_type,
            action_payload=payload,
            approved_yn=True,
            executed_yn=executed_yn,
            result_message=result_message[:500] if result_message else None,
        )
    )


@log_node("Executor")
async def executor_node(state: ChatAgentState) -> dict:
    intent = state.get("intent")
    pending_action = state.get("pending_action", {})
    token = state.get("token")
    account_id = state.get("account_id")

    try:
        if intent == "STOCK":
            stock_info = state.get("stock_info", {})
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
            else:
                price_str = "시장가"
            message = (
                f"✅ 주문 완료\n"
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
            transfer_amount = state.get("amount") or 0
            to_account_number = state.get("to_account_number", "")
            to_bank_code = state.get("to_bank_code", "")
            to_bank_name = _BANK_NAMES.get(to_bank_code, to_bank_code)
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
        _log_action(state, intent, pending_action, executed_yn=False, result_message=message)
        updated_messages = state["messages"] + [{"role": "assistant", "content": message}]
        return {
            "messages": updated_messages,
            "current_task": "executed",
            "pending_action": {},
        }

    _log_action(state, intent, pending_action, executed_yn=True, result_message=message)
    updated_messages = state["messages"] + [{"role": "assistant", "content": message}]

    return {
        "messages": updated_messages,
        "current_task": "executed",
        "pending_action": {},
    }
