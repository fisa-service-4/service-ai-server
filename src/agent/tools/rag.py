import logging
import os

# [BGE-M3] 프로덕션 임베딩 모델 - 빌드 속도 개선을 위해 개발 환경에서 Gemini로 대체
# from FlagEmbedding import BGEM3FlagModel
# _model: BGEM3FlagModel | None = None
# def _get_model() -> BGEM3FlagModel:
#     global _model
#     if _model is None:
#         logger.info("[RAG] BGE-M3 모델 로딩 중...")
#         _model = BGEM3FlagModel("BAAI/bge-m3", use_fp16=True)
#         logger.info("[RAG] BGE-M3 모델 로딩 완료")
#     return _model
# def _embed_query(text: str) -> list[float]:
#     model = _get_model()
#     result = model.encode([text], return_dense=True)
#     return result["dense_vecs"][0].tolist()

from google import genai

from src.pipeline.db import get_vector_pool

logger = logging.getLogger(__name__)

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(
            api_key=os.getenv("LLM_API_KEY"),
            http_options={"api_version": "v1"},
        )
    return _client


def _embed_query(text: str) -> list[float]:
    client = _get_client()
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=[text],
        config={"output_dimensionality": 1024},
    )
    return result.embeddings[0].values


async def search_rag_context(user_id: str, query: str, top_k: int = 5) -> str:
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
              AND indexed_at > NOW() - INTERVAL '3 months'
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
