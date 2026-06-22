# db-analytics-spec.md

# Analytics DB 명세서

분석 DB는 운영 DB의 부하를 분리하고 AI 분석 및 통계 쿼리를 위한 데이터를 저장합니다.

---

## 테이블 목록

| 테이블명                         | 설명           |
|------------------------------|--------------|
| ANALYSIS_RAW_TRANSACTION     | 원천 거래 데이터    |
| ANALYSIS_MONTHLY_INCOME      | 월 수입 분석      |
| ANALYSIS_MONTHLY_EXPENSE     | 월 지출 분석      |
| ANALYSIS_CONSUMPTION_PATTERN | 소비 패턴 분석     |
| ANALYSIS_ASSET_SNAPSHOT      | 자산 스냅샷       |
| ANALYSIS_AI_RECOMMENDATION   | AI 추천 이력     |
| ANALYSIS_AI_BRIEFING_HISTORY | AI 브리핑 이력    |

---

## ANALYSIS_RAW_TRANSACTION

> 운영/은행 거래 데이터를 분석용으로 Sync 저장

| 컬럼명                   | 데이터 타입                           | 설명          | Null 허용 | PK / FK |
|-----------------------|----------------------------------|-------------|---------|---------|
| raw_transaction_id    | BIGINT                           | 원천 거래 ID    | NO      | PK      |
| user_id               | BIGINT                           | 사용자 ID      | NO      | FK      |
| source_type           | ENUM('BANK','CARD','SECURITIES') | 데이터 출처      | NO      | -       |
| source_transaction_id | BIGINT                           | 원본 거래 ID    | NO      | -       |
| account_id            | BIGINT                           | 계좌 ID       | YES     | -       |
| transaction_type      | VARCHAR(50)                      | 거래 유형       | NO      | -       |
| category              | VARCHAR(100)                     | 소비 카테고리     | YES     | -       |
| amount                | DECIMAL(18,2)                    | 거래 금액       | NO      | -       |
| balance_after         | DECIMAL(18,2)                    | 거래 후 잔액     | YES     | -       |
| transaction_at        | TIMESTAMP                        | 거래 시각       | NO      | -       |
| raw_payload           | JSON                             | 원본 JSON 데이터 | NO      | -       |
| synced_at             | TIMESTAMP                        | 동기화 시각      | NO      | -       |

---

## ANALYSIS_MONTHLY_INCOME

> 월별 수입 분석 데이터

| 컬럼명                | 데이터 타입        | 설명            | Null 허용 | PK / FK |
|--------------------|---------------|---------------|---------|---------|
| monthly_income_id  | BIGINT        | 분석 ID         | NO      | PK      |
| user_id            | BIGINT        | 사용자 ID        | NO      | FK      |
| year_month         | VARCHAR(7)    | YYYY-MM       | NO      | -       |
| freelancer_income  | DECIMAL(18,2) | 프리랜서 수입       | YES     | -       |
| salary_income      | DECIMAL(18,2) | 급여 수입 (일단 0원) | YES     | -       |
| investment_income  | DECIMAL(18,2) | 투자 수익 (매도 합계) | YES     | -       |
| etc_income         | DECIMAL(18,2) | 기타 수입         | YES     | -       |
| total_income       | DECIMAL(18,2) | 총 수입          | NO      | -       |
| income_growth_rate | DECIMAL(5,2)  | 수입 증감률        | YES     | -       |
| analyzed_at        | TIMESTAMP     | 분석 시각         | NO      | -       |

---

## ANALYSIS_MONTHLY_EXPENSE

> 월별 지출 분석 데이터

| 컬럼명                   | 데이터 타입        | 설명          | Null 허용 | PK / FK |
|-----------------------|---------------|-------------|---------|---------|
| monthly_expense_id    | BIGINT        | 분석 ID       | NO      | PK      |
| user_id               | BIGINT        | 사용자 ID      | NO      | FK      |
| year_month            | VARCHAR(7)    | YYYY-MM     | NO      | -       |
| food_expense          | DECIMAL(18,2) | 식비          | YES     | -       |
| transport_expense     | DECIMAL(18,2) | 교통비         | YES     | -       |
| shopping_expense      | DECIMAL(18,2) | 쇼핑          | YES     | -       |
| housing_expense       | DECIMAL(18,2) | 주거비         | YES     | -       |
| communication_expense | DECIMAL(18,2) | 통신비         | YES     | -       |
| medical_expense       | DECIMAL(18,2) | 의료비         | YES     | -       |
| investment_expense    | DECIMAL(18,2) | 투자비 (매수 합계) | YES     | -       |
| subscription_expense  | DECIMAL(18,2) | 구독비         | YES     | -       |
| etc_expense           | DECIMAL(18,2) | 기타 지출       | YES     | -       |
| total_expense         | DECIMAL(18,2) | 총 지출        | NO      | -       |
| expense_growth_rate   | DECIMAL(5,2)  | 지출 증감률      | YES     | -       |
| analyzed_at           | TIMESTAMP     | 분석 시각       | NO      | -       |

---

## ANALYSIS_CONSUMPTION_PATTERN

> AI 소비 패턴 분석 결과

| 컬럼명                     | 데이터 타입       | 설명        | Null 허용 | PK / FK |
|-------------------------|--------------|-----------|---------|---------|
| pattern_id              | BIGINT       | 패턴 ID     | NO      | PK      |
| user_id                 | BIGINT       | 사용자 ID    | NO      | FK      |
| consumption_type        | VARCHAR(100) | 소비 유형     | NO      | -       |
| risk_score              | DECIMAL(5,2) | 과소비 위험도   | YES     | -       |
| fixed_expense_ratio     | DECIMAL(5,2) | 고정지출 비율   | YES     | -       |
| impulsive_expense_ratio | DECIMAL(5,2) | 충동소비 비율   | YES     | -       |
| luxury_expense_ratio    | DECIMAL(5,2) | 사치성 소비 비율 | YES     | -       |
| summary                 | TEXT         | AI 분석 요약  | YES     | -       |
| analyzed_at             | TIMESTAMP    | 분석 시각     | NO      | -       |

---

## ANALYSIS_ASSET_SNAPSHOT

> 사용자 자산 스냅샷 저장

| 컬럼명                   | 데이터 타입        | 설명     | Null 허용 | PK / FK |
|-----------------------|---------------|--------|---------|---------|
| snapshot_id           | BIGINT        | 스냅샷 ID | NO      | PK      |
| user_id               | BIGINT        | 사용자 ID | NO      | FK      |
| total_asset           | DECIMAL(18,2) | 총 자산   | NO      | -       |
| total_bank_asset      | DECIMAL(18,2) | 은행 자산  | YES     | -       |
| total_stock_asset     | DECIMAL(18,2) | 증권 자산  | YES     | -       |
| emergency_fund_amount | DECIMAL(18,2) | 비상금    | YES     | -       |
| emergency_fund_ratio  | DECIMAL(5,2)  | 비상금 비율 | YES     | -       |
| snapshot_at           | TIMESTAMP     | 스냅샷 시각 | NO      | -       |

---

## ANALYSIS_AI_RECOMMENDATION

> AI 추천 이력

| 컬럼명                    | 데이터 타입                                            | 설명     | Null 허용 | PK / FK |
|------------------------|---------------------------------------------------|--------|---------|---------|
| recommendation_id      | BIGINT                                            | 추천 ID  | NO      | PK      |
| user_id                | BIGINT                                            | 사용자 ID | NO      | FK      |
| recommendation_type    | ENUM('SALARY','INVESTMENT','CONSUMPTION','STOCK') | 추천 유형  | NO      | -       |
| recommendation_content | TEXT                                              | 추천 내용  | NO      | -       |
| applied_yn             | BOOLEAN                                           | 적용 여부  | NO      | -       |
| created_at             | TIMESTAMP                                         | 생성 시각  | NO      | -       |

---

## ANALYSIS_AI_VECTOR_METADATA

> 벡터 검색 및 LangGraph Memory 저장용 (Vector DB)

| 컬럼명               | 데이터 타입        | 설명          | Null 허용 | PK / FK |
|--------------------|---------------|-------------|---------|---------|
| id                 | BIGSERIAL     | 메타 ID       | NO      | PK      |
| user_id            | BIGINT        | 사용자 ID      | NO      | -       |
| vector_type        | VARCHAR(50)   | 벡터 유형       | NO      | -       |
| reference_id       | BIGINT        | 원본 데이터 ID   | YES     | -       |
| embedding_version  | VARCHAR(50)   | 임베딩 버전      | YES     | -       |
| chunk_text         | TEXT          | 벡터 원문       | YES     | -       |
| vector_key         | VARCHAR(255)  | 벡터 저장 키 (UNIQUE) | YES | -       |
| embedding          | vector(1024)  | pgvector 임베딩 | YES    | -       |
| indexed_at         | TIMESTAMP     | 인덱싱 시각      | NO      | -       |

---

## ANALYSIS_AI_BRIEFING_HISTORY

> AI 브리핑 이력

| 컬럼명                 | 데이터 타입                           | 설명        | Null 허용 | PK / FK |
|---------------------|----------------------------------|-----------|---------|---------|
| briefing_history_id | BIGINT                           | 브리핑 이력 ID | NO      | PK      |
| user_id             | BIGINT                           | 사용자 ID    | NO      | FK      |
| briefing_type       | ENUM('DAILY','WEEKLY','MONTHLY') | 브리핑 유형    | NO      | -       |
| briefing_summary    | TEXT                             | 브리핑 요약    | NO      | -       |
| generated_model     | VARCHAR(100)                     | 생성 모델     | YES     | -       |
| created_at          | TIMESTAMP                        | 생성 시각     | NO      | -       |

