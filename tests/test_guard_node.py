from unittest.mock import AsyncMock, patch

import pytest


def _make_state(intent: str, messages: list | None = None) -> dict:
    return {
        "user_id": "1",
        "session_id": 10,
        "intent": intent,
        "messages": messages or [{"role": "user", "content": "테스트"}],
    }


@pytest.fixture(autouse=True)
def patch_background(monkeypatch):
    monkeypatch.setattr(
        "src.agent.nodes.log_utils.run_in_background", lambda coro: None
    )


class TestGuardNode:
    async def test_unknown_intent_passes_without_policy_check(self):
        with patch("src.agent.nodes.guard.FINANCIAL_POLICIES", []):
            from src.agent.nodes.guard import guard_node
            result = await guard_node(_make_state("UNKNOWN"))
        assert result["guard_passed"] is True
        assert result["guard_reason"] == ""

    async def test_financial_intent_passes_when_no_policies(self):
        with patch("src.agent.nodes.guard.FINANCIAL_POLICIES", []):
            from src.agent.nodes.guard import guard_node
            for intent in ("STOCK", "TRANSFER", "ASSET"):
                result = await guard_node(_make_state(intent))
                assert result["guard_passed"] is True

    async def test_policy_blocks_intent(self):
        async def blocking_policy(state):
            return False, "서비스 이용 불가"

        with patch("src.agent.nodes.guard.FINANCIAL_POLICIES", [blocking_policy]):
            from src.agent.nodes.guard import guard_node
            result = await guard_node(_make_state("STOCK"))

        assert result["guard_passed"] is False
        assert result["guard_reason"] == "서비스 이용 불가"
        assert any(m["role"] == "assistant" for m in result["messages"])

    async def test_policy_passes_intent(self):
        async def passing_policy(state):
            return True, ""

        with patch("src.agent.nodes.guard.FINANCIAL_POLICIES", [passing_policy]):
            from src.agent.nodes.guard import guard_node
            result = await guard_node(_make_state("TRANSFER"))

        assert result["guard_passed"] is True

    async def test_first_failing_policy_blocks(self):
        call_log = []

        async def pass_policy(state):
            call_log.append("pass")
            return True, ""

        async def fail_policy(state):
            call_log.append("fail")
            return False, "차단됨"

        async def never_called_policy(state):
            call_log.append("never")
            return True, ""

        with patch("src.agent.nodes.guard.FINANCIAL_POLICIES", [pass_policy, fail_policy, never_called_policy]):
            from src.agent.nodes.guard import guard_node
            result = await guard_node(_make_state("STOCK"))

        assert result["guard_passed"] is False
        assert "never" not in call_log
