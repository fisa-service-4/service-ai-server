import json
import logging
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


async def _fetch_latest_analysis(conn, user_id: int) -> list[dict]:
    chunks = []

    row = await conn.fetchrow(
        """
        SELECT pattern_id, consumption_type, summary
        FROM analysis_consumption_pattern
        WHERE user_id = $1
        ORDER BY analyzed_at DESC
        LIMIT 1
        """,
        user_id,
    )
    if row and row["summary"]:
        chunks.append({
            "vector_type": "CONSUMPTION_PATTERN",
            "reference_id": row["pattern_id"],
            "chunk_text": f"소비 성향: {row['consumption_type']}\n{row['summary']}",
        })

    row = await conn.fetchrow(
        """
        SELECT briefing_history_id, briefing_summary
        FROM analysis_ai_briefing_history
        WHERE user_id = $1
        ORDER BY created_at DESC
        LIMIT 1
        """,
        user_id,
    )
    if row and row["briefing_summary"]:
        chunks.append({
            "vector_type": "BRIEFING",
            "reference_id": row["briefing_history_id"],
            "chunk_text": row["briefing_summary"],
        })

    rows = await conn.fetch(
        """
        SELECT recommendation_id, recommendation_type, recommendation_content
        FROM analysis_ai_recommendation
        WHERE user_id = $1
        ORDER BY created_at DESC
        LIMIT 4
        """,
        user_id,
    )
    for r in rows:
        content = json.loads(r["recommendation_content"])
        summary = content.get("summary", "")
        if summary:
            chunks.append({
                "vector_type": f"RECOMMENDATION_{r['recommendation_type']}",
                "reference_id": r["recommendation_id"],
                "chunk_text": summary,
            })

    return chunks


async def run(user_id: int):
    analytics_pool = await get_analytics_pool()
    vector_pool = await get_vector_pool()

    async with analytics_pool.acquire() as analytics_conn:
        chunks = await _fetch_latest_analysis(analytics_conn, user_id)

    if not chunks:
        logger.warning("[Embedding] 임베딩할 분석 데이터 없음 - user_id=%s", user_id)
        return

    now = datetime.now()
    year_month = now.strftime("%Y-%m")

    for chunk in chunks:
        chunk["chunk_text"] = f"[{year_month}] {chunk['chunk_text']}"

    texts = [c["chunk_text"] for c in chunks]
    vectors = _embed(texts)

    async with vector_pool.acquire() as vector_conn:
        await vector_conn.execute(
            "DELETE FROM analysis_ai_vector_metadata WHERE user_id = $1 AND indexed_at < NOW() - INTERVAL '3 months'",
            user_id,
        )
        for chunk, vector in zip(chunks, vectors):
            vector_key = f"{user_id}:{chunk['vector_type']}:{year_month}"
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
                chunk["reference_id"],
                EMBEDDING_VERSION,
                chunk["chunk_text"],
                vector_key,
                str(vector),
                now,
            )

    logger.info("[Embedding] 완료 - user_id=%s, chunks=%d", user_id, len(chunks))
