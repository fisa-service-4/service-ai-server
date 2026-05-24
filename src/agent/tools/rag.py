import logging

from FlagEmbedding import BGEM3FlagModel

from src.pipeline.db import get_pool

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
    pool = await get_pool()

    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT vector_type, chunk_text,
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

    if not rows:
        return ""

    context_parts = []
    for row in rows:
        context_parts.append(f"[{row['vector_type']}] {row['chunk_text']}")

    return "\n\n".join(context_parts)
