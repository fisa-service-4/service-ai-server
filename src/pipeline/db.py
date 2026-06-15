import asyncio
import os
import logging

import asyncpg

logger = logging.getLogger(__name__)

_analytics_pool: asyncpg.Pool | None = None
_vector_pool: asyncpg.Pool | None = None
_log_pool: asyncpg.Pool | None = None

_analytics_pool_lock = asyncio.Lock()
_vector_pool_lock = asyncio.Lock()
_log_pool_lock = asyncio.Lock()


async def get_analytics_pool() -> asyncpg.Pool:
    global _analytics_pool
    if _analytics_pool is None:
        async with _analytics_pool_lock:
            if _analytics_pool is None:
                _analytics_pool = await asyncpg.create_pool(
                    host=os.getenv("ANALYTICS_DB_HOST", "localhost"),
                    port=int(os.getenv("ANALYTICS_DB_PORT", "5433")),
                    user=os.getenv("ANALYTICS_DB_USER", "admin"),
                    password=os.getenv("ANALYTICS_DB_PASSWORD", "1234"),
                    database=os.getenv("ANALYTICS_DB_NAME", "finance_analytics"),
                    min_size=2,
                    max_size=10,
                )
    return _analytics_pool


async def get_vector_pool() -> asyncpg.Pool:
    global _vector_pool
    if _vector_pool is None:
        async with _vector_pool_lock:
            if _vector_pool is None:
                _vector_pool = await asyncpg.create_pool(
                    host=os.getenv("VECTOR_DB_HOST", "localhost"),
                    port=int(os.getenv("VECTOR_DB_PORT", "5435")),
                    user=os.getenv("VECTOR_DB_USER", "admin"),
                    password=os.getenv("VECTOR_DB_PASSWORD", "1234"),
                    database=os.getenv("VECTOR_DB_NAME", "finance_vector"),
                    min_size=2,
                    max_size=10,
                    server_settings={"search_path": "public"},
                )
    return _vector_pool


async def get_log_pool() -> asyncpg.Pool:
    global _log_pool
    if _log_pool is None:
        async with _log_pool_lock:
            if _log_pool is None:
                _log_pool = await asyncpg.create_pool(
                    host=os.getenv("LOG_DB_HOST", "localhost"),
                    port=int(os.getenv("LOG_DB_PORT", "5434")),
                    user=os.getenv("LOG_DB_USER", "admin"),
                    password=os.getenv("LOG_DB_PASSWORD", "1234"),
                    database=os.getenv("LOG_DB_NAME", "finance_log"),
                    min_size=2,
                    max_size=10,
                )
    return _log_pool


async def close_pool():
    global _analytics_pool, _vector_pool, _log_pool
    if _analytics_pool:
        await _analytics_pool.close()
        _analytics_pool = None
    if _vector_pool:
        await _vector_pool.close()
        _vector_pool = None
    if _log_pool:
        await _log_pool.close()
        _log_pool = None


async def create_tables():
    analytics_pool = await get_analytics_pool()
    async with analytics_pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS analysis_raw_transaction (
                id                     BIGSERIAL PRIMARY KEY,
                user_id                BIGINT NOT NULL,
                source_type            VARCHAR(50) NOT NULL,
                source_transaction_id  BIGINT NOT NULL,
                account_id             BIGINT,
                transaction_type       VARCHAR(50) NOT NULL,
                category               VARCHAR(100),
                amount                 NUMERIC(18,2) NOT NULL,
                balance_after          NUMERIC(18,2),
                transaction_at         TIMESTAMP NOT NULL,
                raw_payload            JSONB,
                synced_at              TIMESTAMP NOT NULL
            );
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS analysis_asset_snapshot (
                id                     BIGSERIAL PRIMARY KEY,
                user_id                BIGINT NOT NULL,
                total_asset            NUMERIC(18,2) NOT NULL,
                total_bank_asset       NUMERIC(18,2),
                total_stock_asset      NUMERIC(18,2),
                emergency_fund_amount  NUMERIC(18,2),
                emergency_fund_ratio   NUMERIC(5,2),
                snapshot_at            TIMESTAMP NOT NULL
            );
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS analysis_monthly_income (
                id                  BIGSERIAL PRIMARY KEY,
                user_id             BIGINT NOT NULL,
                year_month          VARCHAR(7) NOT NULL,
                freelancer_income   NUMERIC(18,2),
                salary_income       NUMERIC(18,2),
                investment_income   NUMERIC(18,2),
                etc_income          NUMERIC(18,2),
                total_income        NUMERIC(18,2) NOT NULL,
                income_growth_rate  NUMERIC(5,2),
                analyzed_at         TIMESTAMP NOT NULL,
                UNIQUE (user_id, year_month)
            );
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS analysis_monthly_expense (
                id                      BIGSERIAL PRIMARY KEY,
                user_id                 BIGINT NOT NULL,
                year_month              VARCHAR(7) NOT NULL,
                food_expense            NUMERIC(18,2),
                transport_expense       NUMERIC(18,2),
                shopping_expense        NUMERIC(18,2),
                housing_expense         NUMERIC(18,2),
                communication_expense   NUMERIC(18,2),
                medical_expense         NUMERIC(18,2),
                investment_expense      NUMERIC(18,2),
                subscription_expense    NUMERIC(18,2),
                etc_expense             NUMERIC(18,2),
                total_expense           NUMERIC(18,2) NOT NULL,
                expense_growth_rate     NUMERIC(5,2),
                analyzed_at             TIMESTAMP NOT NULL,
                UNIQUE (user_id, year_month)
            );
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS analysis_consumption_pattern (
                pattern_id               BIGSERIAL PRIMARY KEY,
                user_id                  BIGINT NOT NULL,
                consumption_type         VARCHAR(100) NOT NULL,
                risk_score               NUMERIC(5,2),
                fixed_expense_ratio      NUMERIC(5,2),
                impulsive_expense_ratio  NUMERIC(5,2),
                luxury_expense_ratio     NUMERIC(5,2),
                summary                  TEXT,
                analyzed_at              TIMESTAMP NOT NULL
            );
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS analysis_ai_briefing_history (
                briefing_history_id  BIGSERIAL PRIMARY KEY,
                user_id              BIGINT NOT NULL,
                briefing_type        VARCHAR(50) NOT NULL,
                briefing_summary     TEXT NOT NULL,
                generated_model      VARCHAR(100),
                created_at           TIMESTAMP NOT NULL
            );
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS analysis_ai_recommendation (
                recommendation_id       BIGSERIAL PRIMARY KEY,
                user_id                 BIGINT NOT NULL,
                recommendation_type     VARCHAR(50) NOT NULL,
                recommendation_content  TEXT NOT NULL,
                applied_yn              BOOLEAN NOT NULL DEFAULT FALSE,
                created_at              TIMESTAMP NOT NULL
            );
        """)

    vector_pool = await get_vector_pool()
    async with vector_pool.acquire() as conn:
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

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS analysis_ai_vector_metadata (
                id                 BIGSERIAL PRIMARY KEY,
                user_id            BIGINT NOT NULL,
                vector_type        VARCHAR(50) NOT NULL,
                reference_id       BIGINT,
                embedding_version  VARCHAR(50),
                chunk_text         TEXT,
                vector_key         VARCHAR(255) UNIQUE,
                embedding          vector(1024),
                indexed_at         TIMESTAMP NOT NULL
            );
        """)

    log_pool = await get_log_pool()
    async with log_pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS ai_prompt_log (
                prompt_log_id  BIGSERIAL PRIMARY KEY,
                user_id        BIGINT,
                session_id     BIGINT,
                prompt_type    VARCHAR(50)  NOT NULL,
                system_prompt  TEXT,
                user_prompt    TEXT,
                ai_response    TEXT,
                created_at     TIMESTAMP    NOT NULL DEFAULT NOW()
            );
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS ai_action_log (
                ai_action_log_id  BIGSERIAL PRIMARY KEY,
                user_id           BIGINT       NOT NULL,
                action_type       VARCHAR(50)  NOT NULL,
                action_payload    JSONB,
                approved_yn       BOOLEAN      NOT NULL,
                executed_yn       BOOLEAN      NOT NULL,
                result_message    VARCHAR(500),
                created_at        TIMESTAMP    NOT NULL DEFAULT NOW()
            );
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS langgraph_execution_log (
                execution_log_id  BIGSERIAL PRIMARY KEY,
                session_id        BIGINT,
                graph_name        VARCHAR(100) NOT NULL,
                node_name         VARCHAR(100) NOT NULL,
                execution_order   INT          NOT NULL DEFAULT 0,
                execution_result  VARCHAR(100),
                execution_time_ms BIGINT,
                executed_at       TIMESTAMP    NOT NULL DEFAULT NOW()
            );
        """)

    logger.info("[DB] 테이블 초기화 완료")
