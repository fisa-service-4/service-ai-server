import uuid

from src.agent.tools.client import get, post, transaction_get


async def search_stock(query: str, token: str | None = None) -> list:
    result = await transaction_get("/baas/v1/stock/search", token=token, params={"keyword": query})
    return result.get("data", {}).get("content", [])


async def get_stock_price(stock_code: str, token: str | None = None) -> dict:
    result = await transaction_get(f"/baas/v1/stock/{stock_code}/price", token=token)
    return result.get("data", {})


async def get_stocks_accounts(token: str | None = None) -> list:
    result = await get("/api/v1/stocks/accounts", token=token)
    return result.get("data", {}).get("accounts", [])


async def get_holdings(account_id: int = 1, token: str | None = None) -> list:
    result = await get("/api/v1/holdings", token=token, params={"accountId": account_id})
    return result.get("data", {}).get("holdings", [])


async def get_securities_balance(account_id: int = 1, token: str | None = None) -> dict:
    result = await get("/api/v1/stocks/cash-balance", token=token, params={"accountId": account_id})
    return result.get("data", {})


async def execute_buy_order(stock_info: dict, account_id: int, token: str | None = None) -> dict:
    body = {
        "stockCode": stock_info.get("code"),
        "orderType": "BUY",
        "orderMethod": stock_info.get("price_type", "MARKET"),
        "quantity": stock_info.get("quantity"),
        "price": stock_info.get("price"),
    }
    result = await post(
        f"/api/v1/orders?accountId={account_id}",
        token=token,
        body=body,
        extra_headers={"Idempotency-Key": str(uuid.uuid4())},
    )
    return result.get("data", {})


async def execute_sell_order(stock_info: dict, account_id: int, token: str | None = None) -> dict:
    body = {
        "stockCode": stock_info.get("code"),
        "orderType": "SELL",
        "orderMethod": stock_info.get("price_type", "MARKET"),
        "quantity": stock_info.get("quantity"),
        "price": stock_info.get("price"),
    }
    result = await post(
        f"/api/v1/orders?accountId={account_id}",
        token=token,
        body=body,
        extra_headers={"Idempotency-Key": str(uuid.uuid4())},
    )
    return result.get("data", {})
