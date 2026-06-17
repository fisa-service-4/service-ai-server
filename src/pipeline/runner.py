import logging

from src.pipeline.db import get_analytics_pool
from src.pipeline.steps import llm_analysis, stat_analysis, embedding

logger = logging.getLogger(__name__)


async def _fetch_all_user_ids() -> list[int]:
    pool = await get_analytics_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT DISTINCT user_id FROM analysis_raw_transaction ORDER BY user_id"
        )
    return [row["user_id"] for row in rows]


async def run_pipeline_all_users():
    user_ids = await _fetch_all_user_ids()
    if not user_ids:
        logger.warning("[Pipeline] 실행 대상 사용자 없음")
        return
    logger.info("[Pipeline] 전체 사용자 실행 시작 - 대상: %s명", len(user_ids))
    for user_id in user_ids:
        await run_pipeline(user_id)
    logger.info("[Pipeline] 전체 사용자 실행 완료")


async def run_pipeline(user_id: int, max_step: int = 3):
    logger.info("[Pipeline] 시작 - user_id=%s max_step=%s", user_id, max_step)
    try:
        logger.info("[1단계] 월별 수입/지출 통계 집계")
        await stat_analysis.run(user_id)
        logger.info("[1단계] 완료")
        if max_step <= 1:
            return

        logger.info("[2단계] LLM 분석 시작 (시간 소요)")
        await llm_analysis.run(user_id)
        logger.info("[2단계] 완료")
        if max_step <= 2:
            return

        logger.info("[3단계] BGE-M3 임베딩 → pgvector 저장")
        await embedding.run(user_id)
        logger.info("[3단계] 완료")

        logger.info("[Pipeline] 전체 완료 - user_id=%s", user_id)
    except Exception as e:
        logger.exception("[Pipeline] 실행 중 오류 발생 - user_id=%s: %s", user_id, e)
