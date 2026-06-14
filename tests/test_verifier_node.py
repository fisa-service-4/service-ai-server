from unittest.mock import AsyncMock, patch

import pytest


def _make_state(intent: str, messages: list | None = None) -> dict:
    return {
        "user_id": "1",
        "session_id": 10,
        "token": "test-token",
        "intent": intent,
        "messages": messages or [{"role": "user", "content": "확인해줘"}],
    }


@pytest.fixture(autouse=True)
def patch_background(monkeypatch):
    monkeypatch.setattr(
        "src.agent.nodes.log_utils.run_in_background", lambda coro: None
    )


class TestVerifierNode:
    async def test_stock_intent_pin_matched(self):
        with (
            patch("src.agent.nodes.verifier.interrupt", return_value="1234"),
            patch("src.agent.nodes.verifier.verify_pin", AsyncMock(return_value={"matched": True})),
        ):
            from src.agent.nodes.verifier import verifier_node
            result = await verifier_node(_make_state("STOCK"))

        assert result["stock_pin_verified"] is True

    async def test_transfer_intent_pin_matched(self):
        with (
            patch("src.agent.nodes.verifier.interrupt", return_value="1234"),
            patch("src.agent.nodes.verifier.verify_pin", AsyncMock(return_value={"matched": True})),
        ):
            from src.agent.nodes.verifier import verifier_node
            result = await verifier_node(_make_state("TRANSFER"))

        assert result["transfer_pin_verified"] is True

    async def test_asset_intent_pin_matched(self):
        with (
            patch("src.agent.nodes.verifier.interrupt", return_value="1234"),
            patch("src.agent.nodes.verifier.verify_pin", AsyncMock(return_value={"matched": True})),
        ):
            from src.agent.nodes.verifier import verifier_node
            result = await verifier_node(_make_state("ASSET"))

        assert result["apply_pin_verified"] is True

    async def test_pin_not_matched_sets_all_false(self):
        with (
            patch("src.agent.nodes.verifier.interrupt", return_value="0000"),
            patch("src.agent.nodes.verifier.verify_pin", AsyncMock(return_value={"matched": False})),
        ):
            from src.agent.nodes.verifier import verifier_node
            result = await verifier_node(_make_state("STOCK"))

        assert result["stock_pin_verified"] is False
        assert result["transfer_pin_verified"] is False
        assert result["apply_pin_verified"] is False

    async def test_pin_fail_message_for_stock(self):
        with (
            patch("src.agent.nodes.verifier.interrupt", return_value="0000"),
            patch("src.agent.nodes.verifier.verify_pin", AsyncMock(return_value={"matched": False})),
        ):
            from src.agent.nodes.verifier import verifier_node
            result = await verifier_node(_make_state("STOCK"))

        assert "주문" in result["messages"][-1]["content"]

    async def test_pin_fail_message_for_transfer(self):
        with (
            patch("src.agent.nodes.verifier.interrupt", return_value="0000"),
            patch("src.agent.nodes.verifier.verify_pin", AsyncMock(return_value={"matched": False})),
        ):
            from src.agent.nodes.verifier import verifier_node
            result = await verifier_node(_make_state("TRANSFER"))

        assert "이체" in result["messages"][-1]["content"]

    async def test_pin_fail_message_for_asset(self):
        with (
            patch("src.agent.nodes.verifier.interrupt", return_value="0000"),
            patch("src.agent.nodes.verifier.verify_pin", AsyncMock(return_value={"matched": False})),
        ):
            from src.agent.nodes.verifier import verifier_node
            result = await verifier_node(_make_state("ASSET"))

        assert "설정" in result["messages"][-1]["content"]

    async def test_verify_pin_exception_treated_as_failed(self):
        with (
            patch("src.agent.nodes.verifier.interrupt", return_value="1234"),
            patch("src.agent.nodes.verifier.verify_pin", AsyncMock(side_effect=Exception("API 오류"))),
        ):
            from src.agent.nodes.verifier import verifier_node
            result = await verifier_node(_make_state("STOCK"))

        assert result["stock_pin_verified"] is False

    async def test_uses_last_assistant_message_as_interrupt_value(self):
        messages = [
            {"role": "user", "content": "주문할게"},
            {"role": "assistant", "content": "확인 메시지입니다. PIN을 입력해 주세요."},
        ]
        captured = {}

        def mock_interrupt(value):
            captured["value"] = value
            return "1234"

        with (
            patch("src.agent.nodes.verifier.interrupt", side_effect=mock_interrupt),
            patch("src.agent.nodes.verifier.verify_pin", AsyncMock(return_value={"matched": True})),
        ):
            from src.agent.nodes.verifier import verifier_node
            await verifier_node(_make_state("STOCK", messages=messages))

        assert captured["value"] == "확인 메시지입니다. PIN을 입력해 주세요."

    async def test_uses_default_message_when_no_assistant_messages(self):
        messages = [{"role": "user", "content": "주문"}]
        captured = {}

        def mock_interrupt(value):
            captured["value"] = value
            return "1234"

        with (
            patch("src.agent.nodes.verifier.interrupt", side_effect=mock_interrupt),
            patch("src.agent.nodes.verifier.verify_pin", AsyncMock(return_value={"matched": True})),
        ):
            from src.agent.nodes.verifier import verifier_node
            await verifier_node(_make_state("STOCK", messages=messages))

        assert captured["value"] == "PIN을 입력해 주세요."
