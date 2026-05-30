import logging

from src.agent.state import ChatAgentState
from src.agent.tools.stock import get_stock_price, get_securities_balance, get_stocks_accounts, search_stock

logger = logging.getLogger(__name__)


async def stock_check_node(state: ChatAgentState) -> dict:
    stock_info = state.get("stock_info", {})
    stock_code = stock_info.get("code")
    stock_name = stock_info.get("name")
    token = state.get("token")

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

    try:
        price_data = await get_stock_price(stock_code, token=token) if stock_code else {}
        balance_data = await get_securities_balance(token=token)
        accounts = await get_stocks_accounts(token=token)
        account_id = accounts[0]["accountId"] if accounts else None
    except Exception as e:
        logger.error("[StockCheck] 주문 정보 조회 실패: %s", e)
        price_data = {}
        balance_data = {}
        account_id = None

    current_price = price_data.get("currentPrice")
    stock_name = price_data.get("stockName") or stock_info.get("name") or stock_code
    order_type_str = "매수" if stock_info.get("order_type") == "BUY" else "매도"
    quantity = stock_info.get("quantity")
    price_type = stock_info.get("price_type", "MARKET")
    method_str = "시장가" if price_type == "MARKET" else f"지정가 {stock_info.get('price', 0):,}원"

    confirm_msg = f"{stock_name} {quantity}주를 {method_str}로 {order_type_str}하시겠습니까?"
    if current_price:
        confirm_msg += f" (현재가 {current_price:,}원)"
    confirm_msg += " PIN을 입력해 주세요."

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
