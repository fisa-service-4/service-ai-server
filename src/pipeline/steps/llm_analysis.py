import json
import re
from datetime import datetime

from src.agent.llm import MODEL, client
from src.pipeline.db import get_analytics_pool


async def _fetch_monthly_data(conn, user_id: int) -> tuple[list, list]:
    income_rows = await conn.fetch(
        """
        SELECT year_month, freelancer_income, salary_income,
               investment_income, etc_income, total_income, income_growth_rate
        FROM analysis_monthly_income
        WHERE user_id = $1
        ORDER BY year_month
        """,
        user_id,
    )
    expense_rows = await conn.fetch(
        """
        SELECT year_month, food_expense, transport_expense, shopping_expense,
               housing_expense, communication_expense, medical_expense,
               investment_expense, subscription_expense, etc_expense,
               total_expense, expense_growth_rate
        FROM analysis_monthly_expense
        WHERE user_id = $1
        ORDER BY year_month
        """,
        user_id,
    )
    return list(income_rows), list(expense_rows)


def _build_prompt(income_rows: list, expense_rows: list) -> str:
    income_text = "\n".join([
        f"- {r['year_month']}: 총수입 {int(r['total_income']):,}원 "
        f"(프리랜서 {int(r['freelancer_income'] or 0):,} / "
        f"투자수익 {int(r['investment_income'] or 0):,} / "
        f"증감률 {r['income_growth_rate']}%)"
        for r in income_rows
    ])
    expense_text = "\n".join([
        f"- {r['year_month']}: 총지출 {int(r['total_expense']):,}원 "
        f"(식비 {int(r['food_expense'] or 0):,} / "
        f"주거 {int(r['housing_expense'] or 0):,} / "
        f"교통 {int(r['transport_expense'] or 0):,} / "
        f"쇼핑 {int(r['shopping_expense'] or 0):,} / "
        f"의료 {int(r['medical_expense'] or 0):,} / "
        f"구독 {int(r['subscription_expense'] or 0):,} / "
        f"증감률 {r['expense_growth_rate']}%)"
        for r in expense_rows
    ])

    avg_income = sum(float(r["total_income"]) for r in income_rows) / len(income_rows)

    return f"""당신은 프리랜서 전문 AI 금융 어드바이저입니다.
아래 월별 수입/지출 데이터를 분석하고 JSON 형식으로만 응답하세요.

[월별 수입]
{income_text}

[월별 지출]
{expense_text}

[평균 월 수입]
{int(avg_income):,}원

다음 JSON 형식으로 응답하세요. 다른 텍스트는 절대 포함하지 마세요:
{{
  "consumption_pattern": {{
    "consumption_type": "소비 성향 한 줄 요약 (예: 안정형 소비자)",
    "risk_score": 0.0,
    "fixed_expense_ratio": 0.0,
    "impulsive_expense_ratio": 0.0,
    "luxury_expense_ratio": 0.0,
    "summary": "소비 패턴 분석 요약 2~3문장"
  }},
  "briefing": {{
    "briefing_summary": "최근 3개월 종합 금융 브리핑 3~5문장"
  }},
  "recommendations": [
    {{"type": "CONSUMPTION", "summary": "소비 패턴 요약 및 조언 1~2문장", "value": null}},
    {{"type": "SALARY",      "summary": "가상월급 추천 이유 1문장",        "value": "2500000"}},
    {{"type": "INVESTMENT",  "summary": "투자 배분 추천 이유 1문장",       "value": "60"}},
    {{"type": "EMERGENCY",   "summary": "비상금 배분 추천 이유 1문장",     "value": "40"}}
  ]
}}

추천 기준:
- CONSUMPTION: 소비 패턴 요약, value는 null
- SALARY: summary는 추천 이유, value는 권장 가상월급 금액 (원 단위 정수 문자열)
- INVESTMENT: summary는 추천 이유, value는 (수입 - 가상월급) 잔액 중 투자 비율 (0~100 정수 문자열)
- EMERGENCY: summary는 추천 이유, value는 (수입 - 가상월급) 잔액 중 비상금 비율 (0~100 정수 문자열)
- INVESTMENT + EMERGENCY 합계는 반드시 100이어야 함
- risk_score: 0~10 (높을수록 과소비 위험)
- fixed_expense_ratio: 고정지출(주거+통신+구독) 비율 (0~100)
- impulsive_expense_ratio: 충동소비(쇼핑) 비율 (0~100)
- luxury_expense_ratio: 사치성 소비 비율 (0~100)"""


def _parse_llm_response(content: str) -> dict:
    # <think>...</think> 태그 제거 (Qwen3 thinking 모드)
    content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()
    # 코드블록 제거
    content = re.sub(r"```json|```", "", content).strip()
    return json.loads(content)


async def run(user_id: int):
    pool = await get_analytics_pool()

    async with pool.acquire() as conn:
        income_rows, expense_rows = await _fetch_monthly_data(conn, user_id)

        if not income_rows or not expense_rows:
            return

        prompt = _build_prompt(income_rows, expense_rows)

        # LLM 호출 (동기 client를 파이프라인에서 직접 호출)
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        raw = response.choices[0].message.content
        result = _parse_llm_response(raw)

        now = datetime.now()

        # ── 소비 패턴 저장 ─────────────────────────────
        cp = result["consumption_pattern"]
        await conn.execute(
            """
            INSERT INTO analysis_consumption_pattern
                (user_id, consumption_type, risk_score,
                 fixed_expense_ratio, impulsive_expense_ratio, luxury_expense_ratio,
                 summary, analyzed_at)
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8)
            """,
            user_id,
            cp["consumption_type"],
            cp["risk_score"],
            cp["fixed_expense_ratio"],
            cp["impulsive_expense_ratio"],
            cp["luxury_expense_ratio"],
            cp["summary"],
            now,
        )

        # ── 브리핑 저장 ───────────────────────────────
        await conn.execute(
            """
            INSERT INTO analysis_ai_briefing_history
                (user_id, briefing_type, briefing_summary, generated_model, created_at)
            VALUES ($1,$2,$3,$4,$5)
            """,
            user_id,
            "MONTHLY",
            result["briefing"]["briefing_summary"],
            MODEL,
            now,
        )

        # ── 추천 저장 ─────────────────────────────────
        for rec in result["recommendations"]:
            content = json.dumps({
                "summary": rec["summary"],
                "value": rec["value"],
            }, ensure_ascii=False)
            await conn.execute(
                """
                INSERT INTO analysis_ai_recommendation
                    (user_id, recommendation_type, recommendation_content, applied_yn, created_at)
                VALUES ($1,$2,$3,$4,$5)
                """,
                user_id,
                rec["type"],
                content,
                False,
                now,
            )
