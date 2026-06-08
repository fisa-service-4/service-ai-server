import logging

from src.pipeline.mock_data import insert_mock_data
from src.pipeline.steps import llm_analysis, stat_analysis, embedding

logger = logging.getLogger(__name__)


async def run_pipeline(user_id: int, max_step: int = 4):
    logger.info("[Pipeline] 시작 - user_id=%s max_step=%s", user_id, max_step)

    logger.info("[1단계] mock 데이터 INSERT")
    await insert_mock_data(user_id)
    logger.info("[1단계] 완료")
    if max_step <= 1:
        return

    logger.info("[2단계] 월별 수입/지출 통계 집계")
    await stat_analysis.run(user_id)
    logger.info("[2단계] 완료")
    if max_step <= 2:
        return

    logger.info("[3단계] LLM 분석 시작 (시간 소요)")
    await llm_analysis.run(user_id)
    logger.info("[3단계] 완료")
    if max_step <= 3:
        return

    logger.info("[4단계] BGE-M3 임베딩 → pgvector 저장")
    await embedding.run(user_id)
    logger.info("[4단계] 완료")

    logger.info("[Pipeline] 전체 완료 - user_id=%s", user_id)
