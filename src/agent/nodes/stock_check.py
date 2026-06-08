import logging

from src.agent.state import ChatAgentState
from src.agent.tools.stock import get_stock_price, get_securities_balance, get_stocks_accounts, search_stock, get_holdings

logger = logging.getLogger(__name__)


async def stock_check_node(state: ChatAgentState) -> dict:
    stock_info = state.get("stock_info", {})
    stock_code = stock_info.get("code")
    stock_name = stock_info.get("name")
    token = state.get("token")

    if stock_info.get("is_holdings"):
        try:
            accounts = await get_stocks_accounts(token=token) or []
            account_id = accounts[0].get("accountId", 1) if accounts else 1
            holdings = await get_holdings(account_id=account_id, token=token)
            logger.info("[StockCheck] 보유종목 조회 결과: %s", holdings)
        except Exception as e:
            logger.error("[StockCheck] 보유종목 조회 실패: %s", e)
            return {
                "messages": state["messages"] + [{"role": "assistant", "content": f"보유종목 조회 중 오류가 발생했습니다: {e}"}],
                "info_complete": True,
            }

        if not holdings:
            msg = "현재 보유 중인 종목이 없습니다."
        else:
            lines = ["💰 보유 종목 현황"]
            total_eval = 0
            for h in holdings:
                name = h.get("stockName") or h.get("stockCode", "")
                qty = h.get("quantity") or 0
                profit_rate = h.get("profitRate")
                eval_amount = h.get("evaluationAmount") or 0
                total_eval += eval_amount
                value = f"{qty:,}주"
                if profit_rate is not None:
                    sign = "+" if profit_rate >= 0 else ""
                    value += f" ({sign}{profit_rate:.1f}%)"
                lines.append(f"• {name}: {value}")
            if total_eval:
                lines.append(f"총 평가금액 {total_eval:,}원")
            msg = "\n".join(lines)

        return {
            "messages": state["messages"] + [{"role": "assistant", "content": msg}],
            "info_complete": True,
        }

    if stock_info.get("is_inquiry"):
        # 코드가 없으면 이름으로 검색
        if not stock_code and stock_name:
            try:
                results = await search_stock(stock_name, token=token)
                if results:
                    stock_code = results[0].get("stockCode")
                    logger.info("[StockCheck] 검색으로 코드 획득: %s → %s", stock_name, stock_code)
            except Exception as e:
                logger.error("[StockCheck] 종목 검색 실패: %s", e)

        logger.info("[StockCheck] 현재가 조회 시작: stock_code=%s", stock_code)
        try:
            price_data = await get_stock_price(stock_code, token=token) if stock_code else {}
            logger.info("[StockCheck] 현재가 조회 결과: %s", price_data)
        except Exception as e:
            logger.error("[StockCheck] 현재가 조회 실패: %s", e)
            price_data = {}

        stock_name = price_data.get("stockName") or stock_info.get("name") or stock_code
        price = price_data.get("currentPrice")
        change_rate = price_data.get("changeRate")

        if price:
            msg = f"{stock_name}의 현재가는 {price:,}원입니다."
            if change_rate is not None:
                sign = "▲" if change_rate >= 0 else "▼"
                msg += f" ({sign}{abs(change_rate):.2f}%)"
        else:
            msg = f"{stock_name or stock_code}의 현재가를 조회할 수 없습니다."

        updated_messages = state["messages"] + [{"role": "assistant", "content": msg}]
        return {
            "messages": updated_messages,
            "stock_info": {**stock_info, "current_price": price},
            "info_complete": True,
        }

    if not stock_code and not stock_name:
        msg = "어떤 종목을 주문할까요? 종목명이나 종목코드를 알려주세요."
        return {
            "info_complete": False,
            "messages": state["messages"] + [{"role": "assistant", "content": msg}],
        }

    try:
        if not stock_code and stock_name:
            results = await search_stock(stock_name, token=token)
            if results:
                stock_code = results[0].get("stockCode")
                stock_info = {**stock_info, "code": stock_code}
                logger.info("[StockCheck] 주문용 코드 검색: %s → %s", stock_name, stock_code)

        price_data = await get_stock_price(stock_code, token=token) if stock_code else {}
        accounts = await get_stocks_accounts(token=token) or []
        account_id = accounts[0].get("accountId", 1) if accounts else 1
        balance_data = await get_securities_balance(account_id=account_id, token=token)
    except Exception as e:
        logger.error("[StockCheck] 주문 정보 조회 실패: %s", e)
        price_data = {}
        balance_data = {}
        account_id = 1

    current_price = price_data.get("currentPrice")
    stock_name = price_data.get("stockName") or stock_info.get("name") or stock_code
    order_type_str = "매수" if stock_info.get("order_type") == "BUY" else "매도"
    quantity = stock_info.get("quantity")
    price_type = stock_info.get("price_type") or "MARKET"
    method_str = "시장가" if price_type == "MARKET" else f"지정가 {stock_info.get('price') or 0:,}원"

    order_price = stock_info.get("price") if price_type == "LIMIT" else current_price
    total_amount = order_price * quantity if (order_price is not None and quantity is not None) else None
    cash_balance = balance_data.get("cashBalance")
    balance_after = (cash_balance - total_amount) if (cash_balance is not None and total_amount is not None) else None

    lines = [
        "💰 주문 확인",
        f"• 종목: {stock_name}" + (f" ({stock_code})" if stock_code else ""),
        f"• 주문: {method_str} {order_type_str}",
        f"• 수량: {quantity or 0:,}주",
    ]

    if current_price:
        lines.append(f"• 현재가: {current_price:,}원")
    if total_amount:
        lines.append(f"• 예상 금액: {total_amount:,}원")
    if balance_after is not None:
        lines.append(f"• 주문 후 예수금: {balance_after:,}원")
    lines.append("PIN을 입력해 주세요.")

    confirm_msg = "\n".join(lines)

    updated_stock_info = {
        **stock_info,
        "current_price": current_price,
        "cash_balance": balance_data.get("cashBalance"),
        "account_id": account_id,
    }

    updated_messages = state["messages"] + [{"role": "assistant", "content": confirm_msg}]

    return {
        "stock_info": updated_stock_info,
        "info_complete": True,
        "messages": updated_messages,
    }
