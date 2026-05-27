import logging

from FlagEmbedding import BGEM3FlagModel

from src.pipeline.db import get_vector_pool

logger = logging.getLogger(__name__)

_model: BGEM3FlagModel | None = None


def _get_model() -> BGEM3FlagModel:
    global _model
    if _model is None:
        logger.info("[RAG] BGE-M3 모델 로딩 중...")
        _model = BGEM3FlagModel("BAAI/bge-m3", use_fp16=True)
        logger.info("[RAG] BGE-M3 모델 로딩 완료")
    return _model


def _embed_query(text: str) -> list[float]:
    model = _get_model()
    result = model.encode([text], return_dense=True)
    return result["dense_vecs"][0].tolist()


async def search_rag_context(user_id: str, query: str, top_k: int = 3) -> str:
    try:
        uid = int(user_id)
    except (ValueError, TypeError):
        return ""

    vector = _embed_query(query)
    pool = await get_vector_pool()

    async with pool.acquire() as conn:
        personal_rows = await conn.fetch(
            """
            SELECT vector_type AS source, chunk_text,
                   1 - (embedding <=> $1::vector) AS similarity
            FROM analysis_ai_vector_metadata
            WHERE user_id = $2
            ORDER BY embedding <=> $1::vector
            LIMIT $3
            """,
            str(vector),
            uid,
            top_k,
        )

        common_rows = await conn.fetch(
            """
            SELECT category AS source, chunk_text,
                   1 - (embedding <=> $1::vector) AS similarity
            FROM common_knowledge
            ORDER BY embedding <=> $1::vector
            LIMIT $2
            """,
            str(vector),
            top_k,
        )

    all_rows = list(personal_rows) + list(common_rows)
    all_rows.sort(key=lambda r: r["similarity"], reverse=True)
    top_rows = all_rows[:top_k]

    if not top_rows:
        return ""

    return "\n\n".join(f"[{r['source']}] {r['chunk_text']}" for r in top_rows)
