import logging
from decimal import Decimal

from src.agent.state import ChatAgentState
from src.pipeline.db import get_analytics_pool

logger = logging.getLogger(__name__)


def _to_float(value):
    if isinstance(value, Decimal):
        return float(value)
    return value


def _row_to_dict(row) -> dict:
    return {k: _to_float(v) for k, v in dict(row).items()}


async def initialize_node(state: ChatAgentState) -> dict:
    user_id = state.get("user_id")
    analysis_data = {}

    try:
        uid = int(user_id) if user_id else None
        if uid:
            pool = await get_analytics_pool()
            async with pool.acquire() as conn:
                income_row = await conn.fetchrow(
                    """SELECT year_month, freelancer_income, salary_income,
                              investment_income, etc_income, total_income, income_growth_rate
                       FROM analysis_monthly_income
                       WHERE user_id = $1
                       ORDER BY year_month DESC LIMIT 1""",
                    uid,
                )
                if income_row:
                    analysis_data["monthly_income"] = _row_to_dict(income_row)

                expense_row = await conn.fetchrow(
                    """SELECT year_month, food_expense, transport_expense, shopping_expense,
                              housing_expense, communication_expense, medical_expense,
                              investment_expense, subscription_expense, etc_expense,
                              total_expense, expense_growth_rate
                       FROM analysis_monthly_expense
                       WHERE user_id = $1
                       ORDER BY year_month DESC LIMIT 1""",
                    uid,
                )
                if expense_row:
                    analysis_data["monthly_expense"] = _row_to_dict(expense_row)

                pattern_row = await conn.fetchrow(
                    """SELECT consumption_type, risk_score, fixed_expense_ratio,
                              impulsive_expense_ratio, luxury_expense_ratio, summary
                       FROM analysis_consumption_pattern
                       WHERE user_id = $1
                       ORDER BY analyzed_at DESC LIMIT 1""",
                    uid,
                )
                if pattern_row:
                    analysis_data["consumption_pattern"] = _row_to_dict(pattern_row)

                asset_row = await conn.fetchrow(
                    """SELECT total_asset, total_bank_asset, total_stock_asset,
                              emergency_fund_amount, emergency_fund_ratio
                       FROM analysis_asset_snapshot
                       WHERE user_id = $1
                       ORDER BY snapshot_at DESC LIMIT 1""",
                    uid,
                )
                if asset_row:
                    analysis_data["asset_snapshot"] = _row_to_dict(asset_row)

    except Exception:
        logger.exception("[Initialize] 분석 데이터 로딩 실패 (user_id=%s)", user_id)

    return {
        "analysis_data": analysis_data,
        "realtime_data": {},
        "intent": "",
        "current_task": "",
        "rag_context": "",
        "recommended_ratio": {},
        "want_apply": False,
        "apply_confirmed": False,
        "apply_pin_verified": False,
        "stock_info": {},
        "pending_action": {},
        "info_complete": False,
        "confirmed": False,
        "stock_pin_verified": False,
        "need_extra": False,
        "raw_data": {},
        "extra_analysis_data": {},
        "from_account_id": "",
        "to_bank_code": "",
        "to_account_number": "",
        "amount": 0,
        "description": "",
        "transfer_info_complete": False,
        "transfer_confirmed": False,
        "transfer_pin_verified": False,
    }
