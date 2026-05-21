from src.agent.tools.client import get, post


async def search_stock(query: str, token: str | None = None) -> list:
    result = await get("/api/v1/stocks/search", token=token, params={"q": query})
    return result.get("data", [])


async def get_stock_price(stock_code: str, token: str | None = None) -> dict:
    result = await get(f"/api/v1/stocks/{stock_code}/price", token=token)
    return result.get("data", {})


async def get_stocks_accounts(token: str | None = None) -> list:
    result = await get("/api/v1/stocks/accounts", token=token)
    return result.get("data", [])


async def get_securities_balance(token: str | None = None) -> dict:
    result = await get("/api/v1/stocks/cash-balance", token=token)
    return result.get("data", {})


async def execute_buy_order(body: dict, token: str | None = None) -> dict:
    result = await post("/api/v1/orders", token=token, body=body)
    return result.get("data", {})


async def execute_sell_order(body: dict, token: str | None = None) -> dict:
    result = await post("/api/v1/orders", token=token, body={**body, "orderType": "SELL"})
    return result.get("data", {})
