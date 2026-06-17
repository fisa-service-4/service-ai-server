import json
import logging
import re
from datetime import datetime

import os

# [BGE-M3] 프로덕션 임베딩 모델 - 빌드 속도 개선을 위해 개발 환경에서 Gemini로 대체
# from FlagEmbedding import BGEM3FlagModel
# _model: BGEM3FlagModel | None = None
# def _get_model() -> BGEM3FlagModel:
#     global _model
#     if _model is None:
#         logger.info("[Embedding] BGE-M3 모델 로딩 중...")
#         _model = BGEM3FlagModel("BAAI/bge-m3", use_fp16=True)
#         logger.info("[Embedding] BGE-M3 모델 로딩 완료")
#     return _model
# def _embed(texts: list[str]) -> list[list[float]]:
#     model = _get_model()
#     result = model.encode(texts, return_dense=True)
#     return result["dense_vecs"].tolist()

from google import genai

from src.agent.llm import MODEL, client as llm_client
from src.pipeline.db import get_analytics_pool, get_vector_pool

logger = logging.getLogger(__name__)

EMBEDDING_VERSION = "gemini-embedding-004-v1"

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(
            api_key=os.getenv("LLM_API_KEY"),
            http_options={"api_version": "v1"},
        )
    return _client


def _embed(texts: list[str]) -> list[list[float]]:
    client = _get_client()
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=texts,
        config={"output_dimensionality": 1024},
    )
    return [e.values for e in result.embeddings]


async def _fetch_analysis_data(conn, user_id: int) -> dict | None:
    cp_row = await conn.fetchrow(
        """
        SELECT consumption_type, risk_score, fixed_expense_ratio,
               impulsive_expense_ratio, luxury_expense_ratio, summary, analyzed_at
        FROM analysis_consumption_pattern
        WHERE user_id = $1
        ORDER BY analyzed_at DESC
        LIMIT 1
        """,
        user_id,
    )

    br_row = await conn.fetchrow(
        """
        SELECT briefing_summary, created_at
        FROM analysis_ai_briefing_history
        WHERE user_id = $1
        ORDER BY created_at DESC
        LIMIT 1
        """,
        user_id,
    )

    rec_rows = await conn.fetch(
        """
        SELECT recommendation_type, recommendation_content
        FROM analysis_ai_recommendation
        WHERE user_id = $1
        ORDER BY created_at DESC
        LIMIT 4
        """,
        user_id,
    )

    if not cp_row and not br_row:
        return None

    anchor_dt = cp_row["analyzed_at"] if cp_row else br_row["created_at"]

    recommendations = []
    for r in rec_rows:
        content = json.loads(r["recommendation_content"])
        recommendations.append({
            "type": r["recommendation_type"],
            "summary": content.get("summary", ""),
            "value": content.get("value"),
        })

    return {
        "year_month": anchor_dt.strftime("%Y-%m"),
        "consumption_type": cp_row["consumption_type"] if cp_row else None,
        "risk_score": float(cp_row["risk_score"]) if cp_row and cp_row["risk_score"] else None,
        "fixed_expense_ratio": float(cp_row["fixed_expense_ratio"]) if cp_row and cp_row["fixed_expense_ratio"] else None,
        "impulsive_expense_ratio": float(cp_row["impulsive_expense_ratio"]) if cp_row and cp_row["impulsive_expense_ratio"] else None,
        "consumption_summary": cp_row["summary"] if cp_row else None,
        "briefing_summary": br_row["briefing_summary"] if br_row else None,
        "recommendations": recommendations,
    }


def _build_insight_prompt(data: dict) -> str:
    rec_lines = "\n".join(
        f"- [{r['type']}] {r['summary']}" + (f" (추천값: {r['value']}원)" if r.get("value") else "")
        for r in data["recommendations"]
    )
    return f"""다음은 {data['year_month']} 기준 사용자의 AI 금융 분석 결과입니다.

[소비 패턴]
- 성향: {data['consumption_type']}
- 위험점수: {data['risk_score']}/10, 고정지출: {data['fixed_expense_ratio']}%, 충동소비: {data['impulsive_expense_ratio']}%
- 요약: {data['consumption_summary']}

[종합 브리핑]
{data['briefing_summary']}

[AI 추천]
{rec_lines}

위 분석 결과를 바탕으로 다음 두 가지 관점의 인사이트를 각각 2~3문장으로 작성하세요.

인사이트1 (소비 성향 종합): 소비 패턴과 현재 재무 상태를 종합 해석한 서술.
  예시 질문: "내 소비 패턴은?", "내 재무 상황은?"

인사이트2 (개선 포인트): 분석 결과와 추천을 바탕으로 지금 집중해야 할 행동.
  예시 질문: "뭘 바꿔야 해?", "어디서 절약해야 해?"

단순 요약 복사가 아닌, 데이터를 종합해 해석한 통찰 문장이어야 합니다.
JSON으로만 응답:
{{"insight_pattern": "인사이트1 내용", "insight_action": "인사이트2 내용"}}"""


def _parse_insights(content: str) -> dict:
    content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()
    content = re.sub(r"```json|```", "", content).strip()
    return json.loads(content)


async def _synthesize_insights(data: dict) -> list[dict]:
    prompt = _build_insight_prompt(data)
    response = llm_client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    insights = _parse_insights(response.choices[0].message.content)
    year_month = data["year_month"]
    return [
        {
            "vector_type": "INSIGHT_PATTERN",
            "chunk_text": f"[{year_month}] {insights['insight_pattern']}",
            "year_month": year_month,
            "index": 0,
        },
        {
            "vector_type": "INSIGHT_ACTION",
            "chunk_text": f"[{year_month}] {insights['insight_action']}",
            "year_month": year_month,
            "index": 1,
        },
    ]


async def run(user_id: int):
    analytics_pool = await get_analytics_pool()
    vector_pool = await get_vector_pool()

    async with analytics_pool.acquire() as analytics_conn:
        data = await _fetch_analysis_data(analytics_conn, user_id)

    if not data:
        logger.warning("[Embedding] 임베딩할 분석 데이터 없음 - user_id=%s", user_id)
        return

    chunks = await _synthesize_insights(data)

    texts = [c["chunk_text"] for c in chunks]
    vectors = _embed(texts)

    now = datetime.now()

    async with vector_pool.acquire() as vector_conn:
        await vector_conn.execute(
            "DELETE FROM analysis_ai_vector_metadata WHERE user_id = $1 AND indexed_at < NOW() - INTERVAL '3 months'",
            user_id,
        )
        for chunk, vector in zip(chunks, vectors):
            vector_key = f"{user_id}:{chunk['vector_type']}:{chunk['year_month']}"
            await vector_conn.execute(
                "DELETE FROM analysis_ai_vector_metadata WHERE vector_key = $1",
                vector_key,
            )
            await vector_conn.execute(
                """
                INSERT INTO analysis_ai_vector_metadata
                    (user_id, vector_type, reference_id, embedding_version,
                     chunk_text, vector_key, embedding, indexed_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7::vector, $8)
                """,
                user_id,
                chunk["vector_type"],
                None,
                EMBEDDING_VERSION,
                chunk["chunk_text"],
                vector_key,
                str(vector),
                now,
            )

    logger.info("[Embedding] 완료 - user_id=%s, insights=2", user_id)
