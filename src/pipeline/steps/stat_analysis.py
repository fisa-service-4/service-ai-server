from collections import defaultdict
from datetime import datetime

from src.pipeline.db import get_analytics_pool

EXPENSE_COLUMN_MAP = {
    "식비":   "food_expense",
    "교통비": "transport_expense",
    "쇼핑":   "shopping_expense",
    "주거비": "housing_expense",
    "통신비": "communication_expense",
    "의료비": "medical_expense",
    "투자비": "investment_expense",
    "구독":   "subscription_expense",
}

INCOME_COLUMN_MAP = {
    "프리랜서수입": "freelancer_income",
    "급여":        "salary_income",
    "투자수익":    "investment_income",
}


def _growth_rate(current: float, previous: float) -> float | None:
    if previous == 0:
        return None
    return round((current - previous) / previous * 100, 2)


async def run(user_id: int):
    pool = await get_analytics_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT transaction_type, category, amount, transaction_at
            FROM analysis_raw_transaction
            WHERE user_id = $1
            ORDER BY transaction_at
            """,
            user_id,
        )

    # year_month 기준으로 수입/지출 집계
    # income_by_month["2026-03"]["freelancer_income"] = 3200000
    income_by_month: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    expense_by_month: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))

    for row in rows:
        ym = row["transaction_at"].strftime("%Y-%m")
        category = row["category"] or ""
        amount = float(row["amount"])

        if row["transaction_type"] == "INCOME":
            col = INCOME_COLUMN_MAP.get(category, "etc_income")
            income_by_month[ym][col] += amount

        elif row["transaction_type"] == "EXPENSE":
            col = EXPENSE_COLUMN_MAP.get(category, "etc_expense")
            expense_by_month[ym][col] += amount

    sorted_months = sorted(set(list(income_by_month.keys()) + list(expense_by_month.keys())))

    async with pool.acquire() as conn:
        prev_total_income = 0.0
        prev_total_expense = 0.0

        for i, ym in enumerate(sorted_months):
            now = datetime.now()

            # ── 수입 INSERT ──────────────────────────────
            inc = income_by_month[ym]
            total_income = sum(inc.values())
            growth_income = _growth_rate(total_income, prev_total_income) if i > 0 else None

            await conn.execute(
                """
                INSERT INTO analysis_monthly_income
                    (user_id, year_month,
                     freelancer_income, salary_income, investment_income, etc_income,
                     total_income, income_growth_rate, analyzed_at)
                VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)
                ON CONFLICT (user_id, year_month) DO UPDATE SET
                    freelancer_income  = EXCLUDED.freelancer_income,
                    salary_income      = EXCLUDED.salary_income,
                    investment_income  = EXCLUDED.investment_income,
                    etc_income         = EXCLUDED.etc_income,
                    total_income       = EXCLUDED.total_income,
                    income_growth_rate = EXCLUDED.income_growth_rate,
                    analyzed_at        = EXCLUDED.analyzed_at
                """,
                user_id, ym,
                inc.get("freelancer_income") or None,
                inc.get("salary_income") or None,
                inc.get("investment_income") or None,
                inc.get("etc_income") or None,
                total_income,
                growth_income,
                now,
            )

            # ── 지출 INSERT ──────────────────────────────
            exp = expense_by_month[ym]
            total_expense = sum(exp.values())
            growth_expense = _growth_rate(total_expense, prev_total_expense) if i > 0 else None

            await conn.execute(
                """
                INSERT INTO analysis_monthly_expense
                    (user_id, year_month,
                     food_expense, transport_expense, shopping_expense, housing_expense,
                     communication_expense, medical_expense, investment_expense,
                     subscription_expense, etc_expense,
                     total_expense, expense_growth_rate, analyzed_at)
                VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14)
                ON CONFLICT (user_id, year_month) DO UPDATE SET
                    food_expense           = EXCLUDED.food_expense,
                    transport_expense      = EXCLUDED.transport_expense,
                    shopping_expense       = EXCLUDED.shopping_expense,
                    housing_expense        = EXCLUDED.housing_expense,
                    communication_expense  = EXCLUDED.communication_expense,
                    medical_expense        = EXCLUDED.medical_expense,
                    investment_expense     = EXCLUDED.investment_expense,
                    subscription_expense   = EXCLUDED.subscription_expense,
                    etc_expense            = EXCLUDED.etc_expense,
                    total_expense          = EXCLUDED.total_expense,
                    expense_growth_rate    = EXCLUDED.expense_growth_rate,
                    analyzed_at            = EXCLUDED.analyzed_at
                """,
                user_id, ym,
                exp.get("food_expense") or None,
                exp.get("transport_expense") or None,
                exp.get("shopping_expense") or None,
                exp.get("housing_expense") or None,
                exp.get("communication_expense") or None,
                exp.get("medical_expense") or None,
                exp.get("investment_expense") or None,
                exp.get("subscription_expense") or None,
                exp.get("etc_expense") or None,
                total_expense,
                growth_expense,
                now,
            )

            prev_total_income = total_income
            prev_total_expense = total_expense
