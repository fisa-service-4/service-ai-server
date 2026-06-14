from unittest.mock import AsyncMock, patch

import pytest


def _make_state(stock_info: dict, messages: list | None = None) -> dict:
    return {
        "user_id": "1",
        "session_id": 10,
        "token": "test-token",
        "messages": messages or [{"role": "user", "content": "테스트"}],
        "stock_info": stock_info,
    }


@pytest.fixture(autouse=True)
def patch_background(monkeypatch):
    monkeypatch.setattr(
        "src.agent.nodes.log_utils.run_in_background", lambda coro: None
    )


class TestStockCheckNode:
    async def test_holdings_query_returns_holdings_message(self):
        holdings = [
            {"stockName": "삼성전자", "quantity": 10, "profitRate": 3.5, "evaluationAmount": 820000},
        ]
        with (
            patch("src.agent.nodes.stock_check.get_stocks_accounts", AsyncMock(return_value=[{"accountId": 1}])),
            patch("src.agent.nodes.stock_check.get_holdings", AsyncMock(return_value=holdings)),
        ):
            from src.agent.nodes.stock_check import stock_check_node
            result = await stock_check_node(_make_state({"is_holdings": True}))

        assert result["info_complete"] is True
        last_msg = result["messages"][-1]["content"]
        assert "삼성전자" in last_msg
        assert "보유 종목" in last_msg

    async def test_holdings_empty_returns_no_holdings_message(self):
        with (
            patch("src.agent.nodes.stock_check.get_stocks_accounts", AsyncMock(return_value=[{"accountId": 1}])),
            patch("src.agent.nodes.stock_check.get_holdings", AsyncMock(return_value=[])),
        ):
            from src.agent.nodes.stock_check import stock_check_node
            result = await stock_check_node(_make_state({"is_holdings": True}))

        assert "없습니다" in result["messages"][-1]["content"]

    async def test_holdings_api_error_returns_error_message(self):
        with (
            patch("src.agent.nodes.stock_check.get_stocks_accounts", AsyncMock(side_effect=Exception("API 오류"))),
        ):
            from src.agent.nodes.stock_check import stock_check_node
            result = await stock_check_node(_make_state({"is_holdings": True}))

        assert "오류" in result["messages"][-1]["content"]
        assert result["info_complete"] is True

    async def test_inquiry_returns_current_price(self):
        price_data = {"stockName": "삼성전자", "currentPrice": 82000, "changeRate": -1.2}
        with patch("src.agent.nodes.stock_check.get_stock_price", AsyncMock(return_value=price_data)):
            from src.agent.nodes.stock_check import stock_check_node
            result = await stock_check_node(_make_state({
                "is_inquiry": True,
                "code": "005930",
                "name": "삼성전자",
            }))

        last_msg = result["messages"][-1]["content"]
        assert "82,000" in last_msg
        assert result["info_complete"] is True

    async def test_inquiry_without_code_searches_by_name(self):
        search_results = [{"stockCode": "005930"}]
        price_data = {"stockName": "삼성전자", "currentPrice": 82000, "changeRate": 0.5}
        with (
            patch("src.agent.nodes.stock_check.search_stock", AsyncMock(return_value=search_results)),
            patch("src.agent.nodes.stock_check.get_stock_price", AsyncMock(return_value=price_data)),
        ):
            from src.agent.nodes.stock_check import stock_check_node
            result = await stock_check_node(_make_state({
                "is_inquiry": True,
                "code": None,
                "name": "삼성전자",
            }))

        assert result["info_complete"] is True

    async def test_inquiry_price_unavailable(self):
        with patch("src.agent.nodes.stock_check.get_stock_price", AsyncMock(return_value={})):
            from src.agent.nodes.stock_check import stock_check_node
            result = await stock_check_node(_make_state({
                "is_inquiry": True,
                "code": "999999",
                "name": "없는종목",
            }))

        assert "조회할 수 없습니다" in result["messages"][-1]["content"]

    async def test_order_check_builds_confirm_message(self):
        price_data = {"stockName": "삼성전자", "currentPrice": 82000}
        balance_data = {"cashBalance": 1000000}
        with (
            patch("src.agent.nodes.stock_check.get_stock_price", AsyncMock(return_value=price_data)),
            patch("src.agent.nodes.stock_check.get_stocks_accounts", AsyncMock(return_value=[{"accountId": 2}])),
            patch("src.agent.nodes.stock_check.get_securities_balance", AsyncMock(return_value=balance_data)),
        ):
            from src.agent.nodes.stock_check import stock_check_node
            result = await stock_check_node(_make_state({
                "is_holdings": False,
                "is_inquiry": False,
                "code": "005930",
                "name": "삼성전자",
                "quantity": 5,
                "order_type": "BUY",
                "price_type": "MARKET",
                "price": None,
            }))

        msg = result["messages"][-1]["content"]
        assert "주문 확인" in msg
        assert "PIN" in msg
        assert result["info_complete"] is True
        assert result["stock_info"]["account_id"] == 2

    async def test_order_no_code_no_name_asks_for_stock(self):
        from src.agent.nodes.stock_check import stock_check_node
        result = await stock_check_node(_make_state({
            "is_holdings": False,
            "is_inquiry": False,
            "code": None,
            "name": None,
        }))

        assert result["info_complete"] is False
        assert "종목" in result["messages"][-1]["content"]
