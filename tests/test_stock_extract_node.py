import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def _make_state(message: str, stock_info: dict | None = None) -> dict:
    return {
        "user_id": "1",
        "session_id": 10,
        "messages": [{"role": "user", "content": message}],
        "stock_info": stock_info or {},
    }


def _mock_llm_response(payload: dict):
    choice = MagicMock()
    choice.message.content = json.dumps(payload)
    response = MagicMock()
    response.choices = [choice]
    return response


@pytest.fixture(autouse=True)
def patch_background(monkeypatch):
    monkeypatch.setattr(
        "src.agent.nodes.stock_extract.run_in_background", lambda coro: None
    )
    monkeypatch.setattr(
        "src.agent.nodes.stock_extract._insert_prompt_log",
        AsyncMock(),
    )


class TestStockExtractNode:
    async def test_buy_order_complete(self):
        payload = {
            "is_holdings": False,
            "is_inquiry": False,
            "has_order_intent": True,
            "code": "005930",
            "name": "삼성전자",
            "quantity": 10,
            "order_type": "BUY",
            "price_type": "MARKET",
            "price": None,
            "missing": [],
            "question": None,
        }
        with patch("src.agent.nodes.stock_extract.asyncio.to_thread", return_value=_mock_llm_response(payload)):
            from src.agent.nodes.stock_extract import stock_extract_node
            result = await stock_extract_node(_make_state("삼성전자 10주 시장가 매수해줘"))

        assert result["info_complete"] is True
        assert result["stock_info"]["code"] == "005930"
        assert result["stock_info"]["quantity"] == 10
        assert result["stock_info"]["order_type"] == "BUY"

    async def test_inquiry_sets_info_complete(self):
        payload = {
            "is_holdings": False,
            "is_inquiry": True,
            "has_order_intent": False,
            "code": "005930",
            "name": "삼성전자",
            "quantity": None,
            "order_type": None,
            "price_type": None,
            "price": None,
            "missing": [],
            "question": None,
        }
        with patch("src.agent.nodes.stock_extract.asyncio.to_thread", return_value=_mock_llm_response(payload)):
            from src.agent.nodes.stock_extract import stock_extract_node
            result = await stock_extract_node(_make_state("삼성전자 현재가 알려줘"))

        assert result["info_complete"] is True
        assert result["stock_info"]["is_inquiry"] is True

    async def test_holdings_query(self):
        payload = {
            "is_holdings": True,
            "is_inquiry": False,
            "has_order_intent": False,
            "code": None,
            "name": None,
            "quantity": None,
            "order_type": None,
            "price_type": None,
            "price": None,
            "missing": [],
            "question": None,
        }
        with patch("src.agent.nodes.stock_extract.asyncio.to_thread", return_value=_mock_llm_response(payload)):
            from src.agent.nodes.stock_extract import stock_extract_node
            result = await stock_extract_node(_make_state("보유종목 보여줘"))

        assert result["stock_info"]["is_holdings"] is True
        assert result["info_complete"] is True

    async def test_missing_info_appends_question(self):
        payload = {
            "is_holdings": False,
            "is_inquiry": False,
            "has_order_intent": False,
            "code": "005930",
            "name": "삼성전자",
            "quantity": None,
            "order_type": None,
            "price_type": None,
            "price": None,
            "missing": ["quantity", "order_type"],
            "question": "수량과 매수/매도 여부를 알려주세요.",
        }
        with patch("src.agent.nodes.stock_extract.asyncio.to_thread", return_value=_mock_llm_response(payload)):
            from src.agent.nodes.stock_extract import stock_extract_node
            result = await stock_extract_node(_make_state("삼성전자 주문해줘"))

        assert result["info_complete"] is False
        last_msg = result["messages"][-1]
        assert last_msg["role"] == "assistant"
        assert "수량" in last_msg["content"]

    async def test_preserves_prev_stock_info_on_missing(self):
        prev = {"code": "005930", "name": "삼성전자", "quantity": 5, "order_type": "BUY"}
        payload = {
            "is_holdings": False,
            "is_inquiry": False,
            "has_order_intent": True,
            "code": None,
            "name": None,
            "quantity": None,
            "order_type": None,
            "price_type": "MARKET",
            "price": None,
            "missing": [],
            "question": None,
        }
        with patch("src.agent.nodes.stock_extract.asyncio.to_thread", return_value=_mock_llm_response(payload)):
            from src.agent.nodes.stock_extract import stock_extract_node
            result = await stock_extract_node(_make_state("주문할게", stock_info=prev))

        assert result["stock_info"]["code"] == "005930"
        assert result["stock_info"]["quantity"] == 5

    async def test_malformed_json_response_sets_error(self):
        choice = MagicMock()
        choice.message.content = "이건 JSON이 아닙니다"
        response = MagicMock()
        response.choices = [choice]

        with patch("src.agent.nodes.stock_extract.asyncio.to_thread", return_value=response):
            from src.agent.nodes.stock_extract import stock_extract_node
            result = await stock_extract_node(_make_state("주문"))

        assert result["info_complete"] is False
