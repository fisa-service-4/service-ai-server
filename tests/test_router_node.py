from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def _make_state(message: str) -> dict:
    return {
        "user_id": "1",
        "session_id": 10,
        "messages": [{"role": "user", "content": message}],
    }


def _mock_llm_response(content: str):
    choice = MagicMock()
    choice.message.content = content
    response = MagicMock()
    response.choices = [choice]
    return response


@pytest.fixture(autouse=True)
def patch_background(monkeypatch):
    monkeypatch.setattr(
        "src.agent.nodes.router.run_in_background", lambda coro: None
    )
    monkeypatch.setattr(
        "src.agent.nodes.router._insert_prompt_log",
        AsyncMock(),
    )


class TestRouterNode:
    async def test_asset_intent(self):
        with patch("src.agent.nodes.router.asyncio.to_thread", return_value=_mock_llm_response("ASSET")):
            from src.agent.nodes.router import router_node
            result = await router_node(_make_state("이번달 소비 분석해줘"))
        assert result["intent"] == "ASSET"

    async def test_stock_intent(self):
        with patch("src.agent.nodes.router.asyncio.to_thread", return_value=_mock_llm_response("STOCK")):
            from src.agent.nodes.router import router_node
            result = await router_node(_make_state("삼성전자 10주 매수해줘"))
        assert result["intent"] == "STOCK"

    async def test_transfer_intent(self):
        with patch("src.agent.nodes.router.asyncio.to_thread", return_value=_mock_llm_response("TRANSFER")):
            from src.agent.nodes.router import router_node
            result = await router_node(_make_state("50만원 이체해줘"))
        assert result["intent"] == "TRANSFER"

    async def test_unknown_intent_for_invalid_response(self):
        with patch("src.agent.nodes.router.asyncio.to_thread", return_value=_mock_llm_response("GIBBERISH")):
            from src.agent.nodes.router import router_node
            result = await router_node(_make_state("안녕하세요"))
        assert result["intent"] == "UNKNOWN"

    async def test_unknown_intent_for_empty_response(self):
        with patch("src.agent.nodes.router.asyncio.to_thread", return_value=_mock_llm_response("")):
            from src.agent.nodes.router import router_node
            result = await router_node(_make_state("안녕"))
        assert result["intent"] == "UNKNOWN"

    async def test_intent_is_uppercased(self):
        with patch("src.agent.nodes.router.asyncio.to_thread", return_value=_mock_llm_response("  asset  ")):
            from src.agent.nodes.router import router_node
            result = await router_node(_make_state("투자 조언 줘"))
        assert result["intent"] == "ASSET"
