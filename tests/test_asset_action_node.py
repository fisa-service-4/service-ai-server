from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def _make_state(intent: str = "ASSET", message: str = "분배 추천해줘") -> dict:
    return {
        "user_id": "1",
        "session_id": 10,
        "messages": [{"role": "user", "content": message}],
        "intent": intent,
    }


def _mock_llm_response(content: str):
    choice = MagicMock()
    choice.message.content = content
    response = MagicMock()
    response.choices = [choice]
    return response


def _make_recs(salary=3000000, investment=500000, emergency=200000) -> dict:
    return {
        "SALARY": {"value": salary, "summary": "월급 추천"},
        "INVESTMENT": {"value": investment, "summary": ""},
        "EMERGENCY": {"value": emergency, "summary": "비상금 추천"},
    }


@pytest.fixture(autouse=True)
def patch_background(monkeypatch):
    monkeypatch.setattr(
        "src.agent.nodes.asset_action.run_in_background", lambda coro: None
    )
    monkeypatch.setattr(
        "src.agent.nodes.asset_action._insert_prompt_log",
        AsyncMock(),
    )


class TestAssetActionNode:
    async def test_non_asset_intent_returns_consult(self):
        from src.agent.nodes.asset_action import asset_action_node
        result = await asset_action_node({**_make_state(), "intent": "STOCK"})

        assert result["asset_action_type"] == "consult"
        assert result["pending_action"] == {}

    async def test_apply_with_no_recs_returns_error(self):
        with (
            patch("src.agent.nodes.asset_action.asyncio.to_thread", return_value=_mock_llm_response("apply")),
            patch("src.agent.nodes.asset_action._fetch_recommendations", AsyncMock(return_value=None)),
        ):
            from src.agent.nodes.asset_action import asset_action_node
            result = await asset_action_node(_make_state(message="적용해줘"))

        assert result["asset_action_type"] == "apply"
        assert "데이터가 없어요" in result["messages"][-1]["content"]

    async def test_apply_with_recs_returns_confirm_message_and_pending_action(self):
        with (
            patch("src.agent.nodes.asset_action.asyncio.to_thread", return_value=_mock_llm_response("apply")),
            patch("src.agent.nodes.asset_action._fetch_recommendations", AsyncMock(return_value=_make_recs())),
        ):
            from src.agent.nodes.asset_action import asset_action_node
            result = await asset_action_node(_make_state(message="적용해줘"))

        assert result["asset_action_type"] == "apply"
        assert result["pending_action"]["type"] == "VIRTUAL_SALARY"
        assert result["pending_action"]["targetSalary"] == 3000000
        assert "PIN" in result["messages"][-1]["content"]

    async def test_recommend_with_no_recs_returns_error(self):
        with (
            patch("src.agent.nodes.asset_action.asyncio.to_thread", return_value=_mock_llm_response("recommend")),
            patch("src.agent.nodes.asset_action._fetch_recommendations", AsyncMock(return_value=None)),
        ):
            from src.agent.nodes.asset_action import asset_action_node
            result = await asset_action_node(_make_state(message="추천해줘"))

        assert result["asset_action_type"] == "recommend"
        assert "데이터가 없어요" in result["messages"][-1]["content"]

    async def test_recommend_with_recs_returns_recommendation(self):
        with (
            patch("src.agent.nodes.asset_action.asyncio.to_thread", return_value=_mock_llm_response("recommend")),
            patch("src.agent.nodes.asset_action._fetch_recommendations", AsyncMock(return_value=_make_recs())),
        ):
            from src.agent.nodes.asset_action import asset_action_node
            result = await asset_action_node(_make_state(message="추천해줘"))

        assert result["asset_action_type"] == "recommend"
        assert "AI 분배 추천" in result["messages"][-1]["content"]
        assert result["pending_action"] == {}

    async def test_consult_sub_intent_returns_consult_type(self):
        with patch("src.agent.nodes.asset_action.asyncio.to_thread", return_value=_mock_llm_response("consult")):
            from src.agent.nodes.asset_action import asset_action_node
            result = await asset_action_node(_make_state(message="내 자산 어때"))

        assert result["asset_action_type"] == "consult"
        assert result["pending_action"] == {}
