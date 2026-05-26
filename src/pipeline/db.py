import os
import logging

import asyncpg

logger = logging.getLogger(__name__)

_pool: asyncpg.Pool | None = None


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            user=os.getenv("DB_USER", "admin"),
            password=os.getenv("DB_PASSWORD", "1234"),
            database=os.getenv("DB_NAME", "analytics"),
            min_size=2,
            max_size=10,
        )
    return _pool


async def close_pool():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


async def create_tables():
    pool = await get_pool()
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

    logger.info("[DB] 테이블 초기화 완료")
