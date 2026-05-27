"""
공통 금융 지식 문서를 임베딩하여 common_knowledge 테이블에 삽입하는 스크립트.

실행 방법:
    python -m src.pipeline.seed_common_knowledge
"""
import asyncio
import logging

from dotenv import load_dotenv
load_dotenv()

from FlagEmbedding import BGEM3FlagModel

from src.pipeline.data.common_knowledge import DOCUMENTS
from src.pipeline.db import get_vector_pool, close_pool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

EMBEDDING_VERSION = "bge-m3-v1"


def embed_texts(texts: list[str]) -> list[list[float]]:
    logger.info("[Seed] BGE-M3 모델 로딩 중...")
    model = BGEM3FlagModel("BAAI/bge-m3", use_fp16=True)
    logger.info("[Seed] 임베딩 시작 (%d개 문서)", len(texts))
    result = model.encode(texts, return_dense=True, batch_size=8)
    return [vec.tolist() for vec in result["dense_vecs"]]


async def seed():
    pool = await get_vector_pool()

    async with pool.acquire() as conn:
        await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS common_knowledge (
                id                BIGSERIAL PRIMARY KEY,
                category          VARCHAR(100) NOT NULL,
                title             VARCHAR(255),
                chunk_text        TEXT NOT NULL,
                embedding         vector(1024),
                embedding_version VARCHAR(50),
                created_at        TIMESTAMP DEFAULT NOW()
            );
        """)

    texts = [doc["chunk_text"] for doc in DOCUMENTS]
    vectors = embed_texts(texts)

    async with pool.acquire() as conn:
        existing = await conn.fetchval("SELECT COUNT(*) FROM common_knowledge")
        if existing > 0:
            logger.info("[Seed] 이미 %d개 문서가 존재합니다. 중복 삽입을 건너뜁니다.", existing)
            logger.info("[Seed] 전체 재삽입하려면 테이블을 먼저 비워주세요: TRUNCATE common_knowledge;")
            await close_pool()
            return

        rows = [
            (
                doc["category"],
                doc.get("title"),
                doc["chunk_text"],
                str(vec),
                EMBEDDING_VERSION,
            )
            for doc, vec in zip(DOCUMENTS, vectors)
        ]

        await conn.executemany(
            """
            INSERT INTO common_knowledge (category, title, chunk_text, embedding, embedding_version)
            VALUES ($1, $2, $3, $4::vector, $5)
            """,
            rows,
        )

    logger.info("[Seed] 완료: %d개 문서 삽입됨", len(rows))
    await close_pool()


if __name__ == "__main__":
    asyncio.run(seed())
