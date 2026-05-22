import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI

logging.basicConfig(level=logging.INFO)
from fastapi.middleware.cors import CORSMiddleware

from src.api.chat import router as chat_router
from src.pipeline.db import close_pool, get_pool
from src.pipeline.runner import run_pipeline

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await get_pool()
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
async def trigger_pipeline(user_id: int = 1):
    await run_pipeline(user_id)
    return {"status": "ok", "user_id": user_id}
