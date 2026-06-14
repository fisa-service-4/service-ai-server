from unittest.mock import AsyncMock, patch

import pytest


def _make_state(extra: dict | None = None) -> dict:
    state = {
        "user_id": "1",
        "session_id": 10,
        "token": "test-token",
        "messages": [{"role": "user", "content": "이체해줘"}],
        "from_account_id": "",
        "to_bank_code": "",
        "to_account_number": "",
        "amount": 0,
    }
    if extra:
        state.update(extra)
    return state


def _make_account(
    account_id=1001,
    balance=500000,
    role="SALARY",
    bank_code="088",
    account_number="110-111-222",
    account_name="급여통장",
) -> dict:
    return {
        "accountId": account_id,
        "balance": balance,
        "accountRole": role,
        "bankCode": bank_code,
        "accountNumber": account_number,
        "accountName": account_name,
    }


@pytest.fixture(autouse=True)
def patch_background(monkeypatch):
    monkeypatch.setattr(
        "src.agent.nodes.log_utils.run_in_background", lambda coro: None
    )


class TestTransferCheckNode:
    async def test_no_from_account_and_no_accounts_returns_error(self):
        with patch("src.agent.nodes.transfer_check.get_bank_accounts", AsyncMock(return_value=[])):
            from src.agent.nodes.transfer_check import transfer_check_node
            result = await transfer_check_node(_make_state())

        assert result["transfer_info_complete"] is False
        assert "연동된 계좌" in result["messages"][-1]["content"]

    async def test_no_from_account_shows_account_list(self):
        accounts = [_make_account()]
        with patch("src.agent.nodes.transfer_check.get_bank_accounts", AsyncMock(return_value=accounts)):
            from src.agent.nodes.transfer_check import transfer_check_node
            result = await transfer_check_node(_make_state())

        assert result["transfer_info_complete"] is False
        assert result["realtime_data"]["accounts"] == accounts
        assert "출금 계좌 선택" in result["messages"][-1]["content"]

    async def test_insufficient_balance_returns_error(self):
        accounts = [_make_account(account_id=1001, balance=30000)]
        with patch("src.agent.nodes.transfer_check.get_bank_accounts", AsyncMock(return_value=accounts)):
            from src.agent.nodes.transfer_check import transfer_check_node
            result = await transfer_check_node(_make_state({
                "from_account_id": "1001",
                "to_bank_code": "088",
                "to_account_number": "110-123-456789",
                "amount": 100000,
            }))

        assert result["transfer_info_complete"] is False
        assert "잔액이 부족" in result["messages"][-1]["content"]

    async def test_all_complete_builds_confirm_message(self):
        accounts = [_make_account(account_id=1001, balance=500000)]
        with patch("src.agent.nodes.transfer_check.get_bank_accounts", AsyncMock(return_value=accounts)):
            from src.agent.nodes.transfer_check import transfer_check_node
            result = await transfer_check_node(_make_state({
                "from_account_id": "1001",
                "to_bank_code": "088",
                "to_account_number": "110-123-456789",
                "amount": 100000,
            }))

        assert result["transfer_info_complete"] is True
        msg = result["messages"][-1]["content"]
        assert "이체 확인" in msg
        assert "PIN" in msg
        assert "신한은행" in msg

    async def test_get_bank_accounts_exception_treated_as_empty(self):
        with patch("src.agent.nodes.transfer_check.get_bank_accounts", AsyncMock(side_effect=Exception("API 오류"))):
            from src.agent.nodes.transfer_check import transfer_check_node
            result = await transfer_check_node(_make_state())

        assert result["transfer_info_complete"] is False
        assert "연동된 계좌" in result["messages"][-1]["content"]

    async def test_missing_to_bank_code_returns_incomplete(self):
        accounts = [_make_account(account_id=1001, balance=500000)]
        with patch("src.agent.nodes.transfer_check.get_bank_accounts", AsyncMock(return_value=accounts)):
            from src.agent.nodes.transfer_check import transfer_check_node
            result = await transfer_check_node(_make_state({
                "from_account_id": "1001",
                "to_bank_code": "",
                "to_account_number": "110-123-456789",
                "amount": 100000,
            }))

        assert result["transfer_info_complete"] is False
