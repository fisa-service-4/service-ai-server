from unittest.mock import AsyncMock, MagicMock, patch
from decimal import Decimal

import pytest


def _make_state(user_id: str = "1") -> dict:
    return {
        "user_id": user_id,
        "session_id": 10,
        "messages": [{"role": "user", "content": "안녕"}],
    }



@pytest.fixture(autouse=True)
def patch_background(monkeypatch):
    monkeypatch.setattr(
        "src.agent.nodes.log_utils.run_in_background", lambda coro: None
    )


class TestInitializeNode:
    async def test_returns_empty_analysis_when_no_user_id(self):
        with patch("src.agent.nodes.initialize.get_analytics_pool") as mock_pool:
            from src.agent.nodes.initialize import initialize_node
            result = await initialize_node(_make_state(user_id=""))

        assert result["analysis_data"] == {}
        mock_pool.assert_not_called()

    async def test_initializes_all_state_fields(self):
        pool = AsyncMock()
        conn = AsyncMock()
        conn.fetchrow = AsyncMock(return_value=None)
        pool.acquire.return_value.__aenter__ = AsyncMock(return_value=conn)
        pool.acquire.return_value.__aexit__ = AsyncMock(return_value=False)

        with patch("src.agent.nodes.initialize.get_analytics_pool", return_value=pool):
            from src.agent.nodes.initialize import initialize_node
            result = await initialize_node(_make_state())

        assert result["realtime_data"] == {}
        assert result["intent"] == ""
        assert result["current_task"] == ""
        assert result["stock_info"] == {}
        assert result["info_complete"] is False
        assert result["transfer_info_complete"] is False
        assert result["want_apply"] is False

    async def test_loads_analysis_data_from_db(self):
        income_row = {
            "year_month": "2026-05",
            "total_income": Decimal("3000000"),
        }

        pool = MagicMock()
        conn = AsyncMock()
        conn.fetchrow = AsyncMock(side_effect=[income_row, None, None, None])
        pool.acquire.return_value.__aenter__ = AsyncMock(return_value=conn)
        pool.acquire.return_value.__aexit__ = AsyncMock(return_value=False)

        with patch("src.agent.nodes.initialize.get_analytics_pool", new=AsyncMock(return_value=pool)):
            from src.agent.nodes.initialize import initialize_node
            result = await initialize_node(_make_state("42"))

        assert "monthly_income" in result["analysis_data"]
        assert result["analysis_data"]["monthly_income"]["year_month"] == "2026-05"
        assert result["analysis_data"]["monthly_income"]["total_income"] == pytest.approx(3000000.0)

    async def test_returns_empty_analysis_on_db_error(self):
        pool = AsyncMock()
        pool.acquire.side_effect = Exception("DB 연결 실패")

        with patch("src.agent.nodes.initialize.get_analytics_pool", return_value=pool):
            from src.agent.nodes.initialize import initialize_node
            result = await initialize_node(_make_state())

        assert result["analysis_data"] == {}

    def test_to_float_converts_decimal(self):
        from src.agent.nodes.initialize import _to_float
        assert _to_float(Decimal("3.14")) == pytest.approx(3.14)

    def test_to_float_passes_non_decimal(self):
        from src.agent.nodes.initialize import _to_float
        assert _to_float(42) == 42
        assert _to_float("hello") == "hello"
