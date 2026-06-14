from unittest.mock import AsyncMock, patch

import pytest


def _make_stock_state(order_type: str = "BUY", price_type: str = "MARKET") -> dict:
    return {
        "user_id": "1",
        "session_id": 10,
        "token": "test-token",
        "intent": "STOCK",
        "messages": [{"role": "user", "content": "매수해줘"}],
        "pending_action": {},
        "stock_info": {
            "order_type": order_type,
            "code": "005930",
            "name": "삼성전자",
            "quantity": 10,
            "price_type": price_type,
            "price": 80000 if price_type == "LIMIT" else None,
            "account_id": 1,
        },
    }


def _make_transfer_state() -> dict:
    return {
        "user_id": "1",
        "session_id": 10,
        "token": "test-token",
        "intent": "TRANSFER",
        "messages": [{"role": "user", "content": "이체해줘"}],
        "pending_action": {},
        "from_account_id": "1001",
        "to_bank_code": "088",
        "to_account_number": "110-123-456789",
        "amount": 500000,
        "stock_info": {},
    }


def _make_asset_state() -> dict:
    return {
        "user_id": "1",
        "session_id": 10,
        "token": "test-token",
        "intent": "ASSET",
        "messages": [{"role": "user", "content": "적용해줘"}],
        "pending_action": {
            "type": "VIRTUAL_SALARY",
            "targetSalary": 3000000,
            "investmentAmount": 300000,
            "emergencyAmount": 200000,
        },
        "stock_info": {},
    }


@pytest.fixture(autouse=True)
def patch_background(monkeypatch):
    monkeypatch.setattr(
        "src.agent.nodes.executor.run_in_background", lambda coro: None
    )
    monkeypatch.setattr(
        "src.agent.nodes.executor._insert_action_log",
        AsyncMock(),
    )


class TestExecutorNode:
    async def test_buy_order_success(self):
        with patch("src.agent.nodes.executor.execute_buy_order", AsyncMock(return_value={"orderId": 1})):
            from src.agent.nodes.executor import executor_node
            result = await executor_node(_make_stock_state("BUY"))

        msg = result["messages"][-1]["content"]
        assert "주문 완료" in msg
        assert "삼성전자" in msg
        assert result["current_task"] == "executed"

    async def test_sell_order_success(self):
        with patch("src.agent.nodes.executor.execute_sell_order", AsyncMock(return_value={"orderId": 2})):
            from src.agent.nodes.executor import executor_node
            result = await executor_node(_make_stock_state("SELL"))

        msg = result["messages"][-1]["content"]
        assert "주문 완료" in msg
        assert "매도" in msg

    async def test_buy_order_limit_price_shows_price(self):
        with patch("src.agent.nodes.executor.execute_buy_order", AsyncMock(return_value={"orderId": 3})):
            from src.agent.nodes.executor import executor_node
            result = await executor_node(_make_stock_state("BUY", price_type="LIMIT"))

        msg = result["messages"][-1]["content"]
        assert "80,000" in msg

    async def test_transfer_success(self):
        with patch("src.agent.nodes.executor.execute_transfer", AsyncMock(return_value={"transferId": 1})):
            from src.agent.nodes.executor import executor_node
            result = await executor_node(_make_transfer_state())

        msg = result["messages"][-1]["content"]
        assert "이체 완료" in msg
        assert "500,000" in msg

    async def test_asset_virtual_salary_success(self):
        with patch("src.agent.nodes.executor.update_salary_setting", AsyncMock(return_value={"saved": True})):
            from src.agent.nodes.executor import executor_node
            result = await executor_node(_make_asset_state())

        msg = result["messages"][-1]["content"]
        assert "가상월급 설정 완료" in msg
        assert "3,000,000" in msg

    async def test_executor_handles_api_error(self):
        with patch("src.agent.nodes.executor.execute_buy_order", AsyncMock(side_effect=Exception("API 오류"))):
            from src.agent.nodes.executor import executor_node
            result = await executor_node(_make_stock_state("BUY"))

        msg = result["messages"][-1]["content"]
        assert "오류" in msg
        assert result["current_task"] == "executed"
        assert result["pending_action"] == {}

    async def test_pending_action_cleared_after_execution(self):
        with patch("src.agent.nodes.executor.execute_buy_order", AsyncMock(return_value={})):
            from src.agent.nodes.executor import executor_node
            result = await executor_node(_make_stock_state("BUY"))

        assert result["pending_action"] == {}


class TestExecutorHelpers:
    def test_mask_account_number_masks_middle(self):
        from src.agent.nodes.executor import _mask_account_number
        assert _mask_account_number("110-123-456789") == "****6789"

    def test_mask_account_number_short_string(self):
        from src.agent.nodes.executor import _mask_account_number
        assert _mask_account_number("123") == "****"

    def test_mask_account_number_empty(self):
        from src.agent.nodes.executor import _mask_account_number
        assert _mask_account_number("") == "****"

    def test_build_action_payload_stock(self):
        from src.agent.nodes.executor import _build_action_payload
        state = {
            "stock_info": {
                "order_type": "BUY",
                "code": "005930",
                "name": "삼성전자",
                "quantity": 10,
                "price_type": "MARKET",
            }
        }
        payload = _build_action_payload("STOCK", state, {})
        assert payload["orderType"] == "BUY"
        assert payload["stockCode"] == "005930"

    def test_build_action_payload_transfer(self):
        from src.agent.nodes.executor import _build_action_payload
        state = {
            "from_account_id": "1001",
            "to_bank_code": "088",
            "to_account_number": "110-123-456789",
            "amount": 500000,
        }
        payload = _build_action_payload("TRANSFER", state, {})
        assert payload["fromAccountId"] == "1001"
        assert payload["transferAmount"] == 500000
        assert "****" in payload["toAccountNumber"]
