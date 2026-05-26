from src.agent.state import ChatAgentState
from src.agent.tools.stock import get_stock_price, get_securities_balance


async def stock_check_node(state: ChatAgentState) -> dict:
    stock_info = state.get("stock_info", {})
    stock_code = stock_info.get("code")
    token = state.get("token")

    try:
        price_data = await get_stock_price(stock_code, token=token) if stock_code else {}
        balance_data = await get_securities_balance(token=token)
    except Exception:
        price_data = {}
        balance_data = {}

    updated_stock_info = {
        **stock_info,
        "current_price": price_data.get("price"),
        "cash_balance": balance_data.get("cashBalance"),
    }

    return {
        "stock_info": updated_stock_info,
        "info_complete": True,
    }
