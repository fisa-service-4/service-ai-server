import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def _make_state(message: str, extra: dict | None = None) -> dict:
    state = {
        "user_id": "1",
        "session_id": 10,
        "token": "test-token",
        "messages": [{"role": "user", "content": message}],
        "realtime_data": {},
        "from_account_id": "",
        "to_bank_code": "",
        "to_account_number": "",
        "amount": 0,
    }
    if extra:
        state.update(extra)
    return state


def _mock_llm_response(payload: dict):
    choice = MagicMock()
    choice.message.content = json.dumps(payload)
    response = MagicMock()
    response.choices = [choice]
    return response


@pytest.fixture(autouse=True)
def patch_background(monkeypatch):
    monkeypatch.setattr(
        "src.agent.nodes.transfer_extract.run_in_background", lambda coro: None
    )
    monkeypatch.setattr(
        "src.agent.nodes.transfer_extract._insert_prompt_log",
        AsyncMock(),
    )


class TestTransferExtractNode:
    async def test_complete_transfer_info_with_intent(self):
        payload = {
            "has_transfer_intent": True,
            "from_account_id": "1001",
            "to_bank_code": "088",
            "to_account_number": "110-123-456789",
            "amount": 500000,
            "description": "테스트",
            "missing": [],
            "question": None,
        }
        with (
            patch("src.agent.nodes.transfer_extract.get_bank_accounts", AsyncMock(return_value=[])),
            patch("src.agent.nodes.transfer_extract.asyncio.to_thread", return_value=_mock_llm_response(payload)),
        ):
            from src.agent.nodes.transfer_extract import transfer_extract_node
            result = await transfer_extract_node(_make_state("신한은행 110-123-456789로 50만원 이체해줘"))

        assert result["transfer_info_complete"] is True
        assert result["from_account_id"] == "1001"
        assert result["to_bank_code"] == "088"
        assert result["amount"] == 500000

    async def test_fields_complete_but_no_intent_asks_confirmation(self):
        payload = {
            "has_transfer_intent": False,
            "from_account_id": "1001",
            "to_bank_code": "088",
            "to_account_number": "110-123-456789",
            "amount": 500000,
            "description": None,
            "missing": [],
            "question": None,
        }
        with (
            patch("src.agent.nodes.transfer_extract.get_bank_accounts", AsyncMock(return_value=[])),
            patch("src.agent.nodes.transfer_extract.asyncio.to_thread", return_value=_mock_llm_response(payload)),
        ):
            from src.agent.nodes.transfer_extract import transfer_extract_node
            result = await transfer_extract_node(_make_state("신한은행 계좌로 50만원"))

        assert result["transfer_info_complete"] is False
        last_msg = result["messages"][-1]
        assert last_msg["role"] == "assistant"
        assert "이체" in last_msg["content"]

    async def test_missing_fields_appends_question(self):
        payload = {
            "has_transfer_intent": False,
            "from_account_id": None,
            "to_bank_code": None,
            "to_account_number": None,
            "amount": None,
            "description": None,
            "missing": ["to_account_number", "amount"],
            "question": "입금 계좌번호와 금액을 알려주세요.",
        }
        with (
            patch("src.agent.nodes.transfer_extract.get_bank_accounts", AsyncMock(return_value=[])),
            patch("src.agent.nodes.transfer_extract.asyncio.to_thread", return_value=_mock_llm_response(payload)),
        ):
            from src.agent.nodes.transfer_extract import transfer_extract_node
            result = await transfer_extract_node(_make_state("이체해줘"))

        assert result["transfer_info_complete"] is False
        assert "입금 계좌번호" in result["messages"][-1]["content"]

    async def test_preserves_previous_state_fields(self):
        payload = {
            "has_transfer_intent": True,
            "from_account_id": None,
            "to_bank_code": None,
            "to_account_number": None,
            "amount": None,
            "description": None,
            "missing": [],
            "question": None,
        }
        extra = {
            "from_account_id": "1001",
            "to_bank_code": "088",
            "to_account_number": "110-123-456789",
            "amount": 300000,
        }
        with (
            patch("src.agent.nodes.transfer_extract.get_bank_accounts", AsyncMock(return_value=[])),
            patch("src.agent.nodes.transfer_extract.asyncio.to_thread", return_value=_mock_llm_response(payload)),
        ):
            from src.agent.nodes.transfer_extract import transfer_extract_node
            result = await transfer_extract_node(_make_state("이체할게", extra=extra))

        assert result["transfer_info_complete"] is True
        assert result["from_account_id"] == "1001"
        assert result["amount"] == 300000

    async def test_malformed_json_returns_question(self):
        choice = MagicMock()
        choice.message.content = "이건 JSON이 아닙니다"
        response = MagicMock()
        response.choices = [choice]

        with (
            patch("src.agent.nodes.transfer_extract.get_bank_accounts", AsyncMock(return_value=[])),
            patch("src.agent.nodes.transfer_extract.asyncio.to_thread", return_value=response),
        ):
            from src.agent.nodes.transfer_extract import transfer_extract_node
            result = await transfer_extract_node(_make_state("이체"))

        assert result["transfer_info_complete"] is False

    async def test_loads_accounts_if_not_in_state(self):
        accounts = [{"accountId": 1001, "accountName": "급여통장", "accountNumber": "110-111-222"}]
        payload = {
            "has_transfer_intent": False,
            "from_account_id": None,
            "to_bank_code": None,
            "to_account_number": None,
            "amount": None,
            "description": None,
            "missing": ["amount"],
            "question": "금액을 알려주세요.",
        }
        with (
            patch("src.agent.nodes.transfer_extract.get_bank_accounts", AsyncMock(return_value=accounts)) as mock_accounts,
            patch("src.agent.nodes.transfer_extract.asyncio.to_thread", return_value=_mock_llm_response(payload)),
        ):
            from src.agent.nodes.transfer_extract import transfer_extract_node
            result = await transfer_extract_node(_make_state("이체하고 싶어"))

        mock_accounts.assert_called_once()
        assert result["realtime_data"]["accounts"] == accounts
