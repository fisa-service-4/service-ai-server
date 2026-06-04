import json
import logging
from contextlib import asynccontextmanager
from typing import Optional

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)

from src.api.chat import router as chat_router
from src.api.response import ok, fail
from src.pipeline.db import close_pool, create_tables, get_analytics_pool
from src.pipeline.runner import run_pipeline

logger = logging.getLogger(__name__)


class RecommendationRequest(BaseModel):
    userId: Optional[int] = 1


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield
    await close_pool()


app = FastAPI(
    title="AI Server",
    description="AI 기반 자산 분석 및 리포트 생성 서버",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/api/v1/admin/pipeline/run")
async def trigger_pipeline(user_id: int = 1, max_step: int = 4):
    await run_pipeline(user_id, max_step=max_step)
    return {"status": "ok", "user_id": user_id, "max_step": max_step}


@app.post("/virtual-salary/recommend")
async def recommend_virtual_salary(request: RecommendationRequest):
    try:
        user_id = request.userId or 1
        pool = await get_analytics_pool()

        async with pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT DISTINCT ON (recommendation_type)
                    recommendation_type, recommendation_content
                FROM analysis_ai_recommendation
                WHERE user_id = $1
                ORDER BY recommendation_type, created_at DESC
                """,
                user_id,
            )

        if not rows:
            return fail("AI_001", "추천 데이터가 없습니다. 파이프라인을 먼저 실행해주세요.")

        recs = {row["recommendation_type"]: json.loads(row["recommendation_content"]) for row in rows}

        salary_rec = recs.get("SALARY", {})
        emergency_rec = recs.get("EMERGENCY", {})
        investment_rec = recs.get("INVESTMENT", {})

        def safe_int(val):
            try:
                return int(val) if val is not None else None
            except (ValueError, TypeError):
                return None

        summaries = [s for s in [salary_rec.get("summary"), emergency_rec.get("summary")] if s]

        return ok({
            "recommendedTargetSalary": safe_int(salary_rec.get("value")),
            "recommendedEmergencyAmount": safe_int(emergency_rec.get("value")),
            "recommendedInvestmentAmount": safe_int(investment_rec.get("value")),
            "summary": " ".join(summaries),
        })

    except Exception as e:
        logger.error("[Recommendation] 추천 조회 실패: %s", e)
        return fail("AI_001", "추천 데이터 조회에 실패했습니다.")
