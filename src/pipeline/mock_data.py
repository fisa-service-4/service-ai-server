import json
from datetime import datetime

from src.pipeline.db import get_pool

# user_id=1 기준 3개월치 거래 mock 데이터
# source_transaction_id는 원본 운영 DB의 거래 ID를 의미 (여기선 임의 부여)
MOCK_TRANSACTIONS = [
    # ── 2026-02 ──────────────────────────────────────────
    # 수입
    {"source_transaction_id": 1001, "transaction_type": "INCOME",  "category": "프리랜서수입", "amount": 2500000, "source_type": "BANK",       "transaction_at": "2026-02-05 09:00:00"},
    # 지출
    {"source_transaction_id": 1002, "transaction_type": "EXPENSE", "category": "식비",       "amount":   85000, "source_type": "CARD",       "transaction_at": "2026-02-07 12:30:00"},
    {"source_transaction_id": 1003, "transaction_type": "EXPENSE", "category": "식비",       "amount":   72000, "source_type": "CARD",       "transaction_at": "2026-02-14 19:00:00"},
    {"source_transaction_id": 1004, "transaction_type": "EXPENSE", "category": "식비",       "amount":   93000, "source_type": "CARD",       "transaction_at": "2026-02-21 13:00:00"},
    {"source_transaction_id": 1005, "transaction_type": "EXPENSE", "category": "주거비",     "amount":  500000, "source_type": "BANK",       "transaction_at": "2026-02-10 09:00:00"},
    {"source_transaction_id": 1006, "transaction_type": "EXPENSE", "category": "교통비",     "amount":   38000, "source_type": "CARD",       "transaction_at": "2026-02-12 08:00:00"},
    {"source_transaction_id": 1007, "transaction_type": "EXPENSE", "category": "교통비",     "amount":   42000, "source_type": "CARD",       "transaction_at": "2026-02-24 08:00:00"},
    {"source_transaction_id": 1008, "transaction_type": "EXPENSE", "category": "통신비",     "amount":   55000, "source_type": "BANK",       "transaction_at": "2026-02-15 09:00:00"},
    {"source_transaction_id": 1009, "transaction_type": "EXPENSE", "category": "쇼핑",       "amount":   67000, "source_type": "CARD",       "transaction_at": "2026-02-18 16:00:00"},
    {"source_transaction_id": 1010, "transaction_type": "EXPENSE", "category": "쇼핑",       "amount":   53000, "source_type": "CARD",       "transaction_at": "2026-02-25 15:00:00"},
    {"source_transaction_id": 1011, "transaction_type": "EXPENSE", "category": "구독",       "amount":   15000, "source_type": "CARD",       "transaction_at": "2026-02-01 00:00:00"},

    # ── 2026-03 ──────────────────────────────────────────
    # 수입
    {"source_transaction_id": 2001, "transaction_type": "INCOME",  "category": "프리랜서수입", "amount": 3200000, "source_type": "BANK",       "transaction_at": "2026-03-10 09:00:00"},
    # 지출
    {"source_transaction_id": 2002, "transaction_type": "EXPENSE", "category": "식비",       "amount":   98000, "source_type": "CARD",       "transaction_at": "2026-03-05 12:00:00"},
    {"source_transaction_id": 2003, "transaction_type": "EXPENSE", "category": "식비",       "amount":  112000, "source_type": "CARD",       "transaction_at": "2026-03-13 19:30:00"},
    {"source_transaction_id": 2004, "transaction_type": "EXPENSE", "category": "식비",       "amount":  100000, "source_type": "CARD",       "transaction_at": "2026-03-22 12:30:00"},
    {"source_transaction_id": 2005, "transaction_type": "EXPENSE", "category": "주거비",     "amount":  500000, "source_type": "BANK",       "transaction_at": "2026-03-10 09:00:00"},
    {"source_transaction_id": 2006, "transaction_type": "EXPENSE", "category": "교통비",     "amount":   45000, "source_type": "CARD",       "transaction_at": "2026-03-08 08:00:00"},
    {"source_transaction_id": 2007, "transaction_type": "EXPENSE", "category": "교통비",     "amount":   45000, "source_type": "CARD",       "transaction_at": "2026-03-20 08:00:00"},
    {"source_transaction_id": 2008, "transaction_type": "EXPENSE", "category": "통신비",     "amount":   55000, "source_type": "BANK",       "transaction_at": "2026-03-15 09:00:00"},
    {"source_transaction_id": 2009, "transaction_type": "EXPENSE", "category": "쇼핑",       "amount":  135000, "source_type": "CARD",       "transaction_at": "2026-03-16 14:00:00"},
    {"source_transaction_id": 2010, "transaction_type": "EXPENSE", "category": "쇼핑",       "amount":   65000, "source_type": "CARD",       "transaction_at": "2026-03-27 17:00:00"},
    {"source_transaction_id": 2011, "transaction_type": "EXPENSE", "category": "의료비",     "amount":   45000, "source_type": "CARD",       "transaction_at": "2026-03-19 11:00:00"},
    {"source_transaction_id": 2012, "transaction_type": "EXPENSE", "category": "구독",       "amount":   15000, "source_type": "CARD",       "transaction_at": "2026-03-01 00:00:00"},

    # ── 2026-04 ──────────────────────────────────────────
    # 수입
    {"source_transaction_id": 3001, "transaction_type": "INCOME",  "category": "프리랜서수입", "amount": 2800000, "source_type": "BANK",       "transaction_at": "2026-04-08 09:00:00"},
    {"source_transaction_id": 3002, "transaction_type": "INCOME",  "category": "투자수익",   "amount":  150000, "source_type": "SECURITIES", "transaction_at": "2026-04-15 10:00:00"},
    # 지출
    {"source_transaction_id": 3003, "transaction_type": "EXPENSE", "category": "식비",       "amount":   88000, "source_type": "CARD",       "transaction_at": "2026-04-04 12:00:00"},
    {"source_transaction_id": 3004, "transaction_type": "EXPENSE", "category": "식비",       "amount":   95000, "source_type": "CARD",       "transaction_at": "2026-04-17 19:00:00"},
    {"source_transaction_id": 3005, "transaction_type": "EXPENSE", "category": "식비",       "amount":   97000, "source_type": "CARD",       "transaction_at": "2026-04-25 13:00:00"},
    {"source_transaction_id": 3006, "transaction_type": "EXPENSE", "category": "주거비",     "amount":  500000, "source_type": "BANK",       "transaction_at": "2026-04-10 09:00:00"},
    {"source_transaction_id": 3007, "transaction_type": "EXPENSE", "category": "교통비",     "amount":   47000, "source_type": "CARD",       "transaction_at": "2026-04-07 08:00:00"},
    {"source_transaction_id": 3008, "transaction_type": "EXPENSE", "category": "교통비",     "amount":   48000, "source_type": "CARD",       "transaction_at": "2026-04-21 08:00:00"},
    {"source_transaction_id": 3009, "transaction_type": "EXPENSE", "category": "통신비",     "amount":   55000, "source_type": "BANK",       "transaction_at": "2026-04-15 09:00:00"},
    {"source_transaction_id": 3010, "transaction_type": "EXPENSE", "category": "쇼핑",       "amount":   75000, "source_type": "CARD",       "transaction_at": "2026-04-19 15:00:00"},
    {"source_transaction_id": 3011, "transaction_type": "EXPENSE", "category": "쇼핑",       "amount":   75000, "source_type": "CARD",       "transaction_at": "2026-04-28 16:00:00"},
    {"source_transaction_id": 3012, "transaction_type": "EXPENSE", "category": "구독",       "amount":   15000, "source_type": "CARD",       "transaction_at": "2026-04-01 00:00:00"},
]

MOCK_ASSET_SNAPSHOT = {
    "total_asset":           35000000,
    "total_bank_asset":      20000000,
    "total_stock_asset":     15000000,
    "emergency_fund_amount":  5000000,
    "emergency_fund_ratio":      14.3,
    "snapshot_at":       "2026-04-30 23:59:00",
}


async def insert_mock_data():
    pool = await get_pool()
    async with pool.acquire() as conn:
        # 중복 방지: 이미 데이터가 있으면 스킵
        count = await conn.fetchval("SELECT COUNT(*) FROM analysis_raw_transaction WHERE user_id = 1")
        if count > 0:
            return

        now = datetime.now()
        for tx in MOCK_TRANSACTIONS:
            await conn.execute(
                """
                INSERT INTO analysis_raw_transaction
                    (user_id, source_type, source_transaction_id, account_id,
                     transaction_type, category, amount, balance_after,
                     transaction_at, raw_payload, synced_at)
                VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11)
                """,
                1,
                tx["source_type"],
                tx["source_transaction_id"],
                1001,
                tx["transaction_type"],
                tx["category"],
                tx["amount"],
                None,
                datetime.strptime(tx["transaction_at"], "%Y-%m-%d %H:%M:%S"),
                json.dumps(tx),
                now,
            )

        s = MOCK_ASSET_SNAPSHOT
        await conn.execute(
            """
            INSERT INTO analysis_asset_snapshot
                (user_id, total_asset, total_bank_asset, total_stock_asset,
                 emergency_fund_amount, emergency_fund_ratio, snapshot_at)
            VALUES ($1,$2,$3,$4,$5,$6,$7)
            """,
            1,
            s["total_asset"],
            s["total_bank_asset"],
            s["total_stock_asset"],
            s["emergency_fund_amount"],
            s["emergency_fund_ratio"],
            datetime.strptime(s["snapshot_at"], "%Y-%m-%d %H:%M:%S"),
        )
