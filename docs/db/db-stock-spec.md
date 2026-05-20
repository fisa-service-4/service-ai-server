# db-stock-spec.md

# Stock DB 명세서

증권 DB는 증권 계좌, 주문, 체결, 보유 종목, 포트폴리오 데이터를 관리합니다.

금융 거래 특성상 주문(Order)과 체결(Execution)을 분리하여 관리하며,
모든 주문 변경 이력을 별도로 저장합니다.

---

## 테이블 목록

| 테이블명                       | 설명          |
|----------------------------|-------------|
| SECURITIES_ACCOUNT         | 증권 계좌 정보    |
| STOCK_MASTER               | 종목 마스터 정보   |
| STOCK_PRICE_HISTORY        | 종목 시세 이력    |
| STOCK_ORDER                | 주식 주문 정보    |
| STOCK_EXECUTION            | 주식 체결 정보    |
| STOCK_HOLDING              | 보유 종목 정보    |
| STOCK_PORTFOLIO_SNAPSHOT   | 포트폴리오 스냅샷   |
| ORDER_MODIFICATION_HISTORY | 주문 정정/취소 이력 |

---

## SECURITIES_ACCOUNT

> 증권 계좌 정보를 저장합니다.

| 컬럼명                   | 데이터 타입        | 설명       | Null 허용 | PK / FK |
|-----------------------|---------------|----------|---------|---------|
| securities_account_id | BIGINT        | 증권 계좌 ID | NO      | PK      |
| user_id               | BIGINT        | 사용자 ID   | NO      | -       |
| broker_code           | VARCHAR(20)   | 증권사 코드   | NO      | -       |
| account_number        | VARCHAR(50)   | 증권 계좌번호  | NO      | UNIQUE  |
| account_name          | VARCHAR(100)  | 계좌명      | NO      | -       |
| cash_balance          | DECIMAL(18,2) | 예수금      | NO      | -       |
| withdrawable_balance  | DECIMAL(18,2) | 출금 가능 금액 | NO      | -       |
| total_evaluated_asset | DECIMAL(18,2) | 총 평가 자산  | YES     | -       |
| account_status        | ENUM          | 계좌 상태    | NO      | -       |
| opened_at             | TIMESTAMP     | 계좌 개설일   | NO      | -       |
| closed_at             | TIMESTAMP     | 계좌 해지일   | YES     | -       |
| updated_at            | TIMESTAMP     | 수정일      | YES     | -       |

### account_status

| 값      | 설명 |
|--------|----|
| ACTIVE | 정상 |
| LOCKED | 잠금 |
| CLOSED | 해지 |

---

## STOCK_MASTER

> 종목 마스터 정보를 저장합니다.

| 컬럼명         | 데이터 타입       | 설명    | Null 허용 | PK / FK |
|-------------|--------------|-------|---------|---------|
| stock_code  | VARCHAR(20)  | 종목 코드 | NO      | PK      |
| stock_name  | VARCHAR(255) | 종목명   | NO      | -       |
| market_type | ENUM         | 시장 구분 | NO      | -       |

### market_type

| 값      | 설명      |
|--------|---------|
| KOSPI  | 코스피     |
| KOSDAQ | 코스닥     |
| NASDAQ | 나스닥     |
| NYSE   | 뉴욕증권거래소 |
| ETF    | ETF     |

---

## STOCK_PRICE_HISTORY

> 종목 시세 이력을 저장합니다.

| 컬럼명              | 데이터 타입        | 설명        | Null 허용 | PK / FK |
|------------------|---------------|-----------|---------|---------|
| price_history_id | BIGINT        | 시세 이력 ID  | NO      | PK      |
| stock_code       | VARCHAR(20)   | 종목 코드     | NO      | FK      |
| traded_date      | DATE          | 거래일       | NO      | -       |
| open_price       | DECIMAL(18,2) | 시가        | YES     | -       |
| high_price       | DECIMAL(18,2) | 고가        | YES     | -       |
| low_price        | DECIMAL(18,2) | 저가        | YES     | -       |
| close_price      | DECIMAL(18,2) | 종가        | YES     | -       |
| volume           | BIGINT        | 거래량       | YES     | -       |
| fluctuation_rate | DECIMAL(5,2)  | 등락률       | YES     | -       |
| market_cap       | DECIMAL(18,2) | 시가총액      | YES     | -       |
| collected_at     | TIMESTAMP     | 데이터 수집 시각 | NO      | -       |

---

## STOCK_ORDER

> 주식 주문 정보를 저장합니다.

| 컬럼명                     | 데이터 타입        | 설명       | Null 허용 | PK / FK |
|-------------------------|---------------|----------|---------|---------|
| stock_order_id          | BIGINT        | 주문 ID    | NO      | PK      |
| securities_account_id   | BIGINT        | 증권 계좌 ID | NO      | FK      |
| stock_code              | VARCHAR(20)   | 종목 코드    | NO      | FK      |
| order_type              | ENUM          | 주문 유형    | NO      | -       |
| order_method            | ENUM          | 주문 방식    | NO      | -       |
| order_price             | DECIMAL(18,2) | 주문 가격    | YES     | -       |
| order_quantity          | INT           | 주문 수량    | NO      | -       |
| filled_quantity         | INT           | 체결 수량    | YES     | -       |
| remaining_quantity      | INT           | 미체결 수량   | YES     | -       |
| average_execution_price | DECIMAL(18,2) | 평균 체결가   | YES     | -       |
| order_status            | ENUM          | 주문 상태    | NO      | -       |
| ordered_by              | ENUM          | 주문 주체    | NO      | -       |
| ordered_at              | TIMESTAMP     | 주문 시각    | NO      | -       |
| updated_at              | TIMESTAMP     | 수정일      | YES     | -       |

### order_type

| 값    | 설명 |
|------|----|
| BUY  | 매수 |
| SELL | 매도 |

### order_method

| 값      | 설명  |
|--------|-----|
| MARKET | 시장가 |
| LIMIT  | 지정가 |

### order_status

| 값              | 설명    |
|----------------|-------|
| REQUESTED      | 주문 요청 |
| PARTIAL_FILLED | 부분 체결 |
| FILLED         | 전체 체결 |
| CANCELLED      | 주문 취소 |
| FAILED         | 주문 실패 |

### ordered_by

| 값    | 설명       |
|------|----------|
| USER | 사용자      |
| AI   | AI 자동 주문 |

---

## STOCK_EXECUTION

> 주식 체결 정보를 저장합니다.

| 컬럼명               | 데이터 타입        | 설명    | Null 허용 | PK / FK |
|-------------------|---------------|-------|---------|---------|
| execution_id      | BIGINT        | 체결 ID | NO      | PK      |
| stock_order_id    | BIGINT        | 주문 ID | NO      | FK      |
| stock_code        | VARCHAR(20)   | 종목 코드 | NO      | FK      |
| executed_price    | DECIMAL(18,2) | 체결 가격 | NO      | -       |
| executed_quantity | INT           | 체결 수량 | NO      | -       |
| execution_amount  | DECIMAL(18,2) | 체결 금액 | NO      | -       |
| executed_at       | TIMESTAMP     | 체결 시각 | NO      | -       |

---

## STOCK_HOLDING

> 보유 종목 정보를 저장합니다.

| 컬럼명                    | 데이터 타입        | 설명       | Null 허용 | PK / FK |
|------------------------|---------------|----------|---------|---------|
| holding_id             | BIGINT        | 보유 종목 ID | NO      | PK      |
| securities_account_id  | BIGINT        | 증권 계좌 ID | NO      | FK      |
| stock_code             | VARCHAR(20)   | 종목 코드    | NO      | FK      |
| holding_quantity       | INT           | 보유 수량    | NO      | -       |
| average_purchase_price | DECIMAL(18,2) | 평균 매입가   | NO      | -       |
| total_purchase_amount  | DECIMAL(18,2) | 총 매입 금액  | YES     | -       |
| evaluated_amount       | DECIMAL(18,2) | 평가 금액    | YES     | -       |
| unrealized_profit      | DECIMAL(18,2) | 미실현 손익   | YES     | -       |
| profit_rate            | DECIMAL(5,2)  | 수익률      | YES     | -       |
| updated_at             | TIMESTAMP     | 수정일      | NO      | -       |

---

## STOCK_PORTFOLIO_SNAPSHOT

> 포트폴리오 스냅샷 데이터를 저장합니다.

| 컬럼명               | 데이터 타입        | 설명     | Null 허용 | PK / FK |
|-------------------|---------------|--------|---------|---------|
| snapshot_id       | BIGINT        | 스냅샷 ID | NO      | PK      |
| user_id           | BIGINT        | 사용자 ID | NO      | -       |
| total_asset       | DECIMAL(18,2) | 총 자산   | YES     | -       |
| stock_asset       | DECIMAL(18,2) | 주식 자산  | YES     | -       |
| cash_asset        | DECIMAL(18,2) | 현금 자산  | YES     | -       |
| total_profit      | DECIMAL(18,2) | 총 손익   | YES     | -       |
| total_profit_rate | DECIMAL(5,2)  | 총 수익률  | YES     | -       |
| snapshot_date     | DATE          | 기준 일자  | NO      | -       |
| created_at        | TIMESTAMP     | 생성일    | NO      | -       |

---

## ORDER_MODIFICATION_HISTORY

> 주문 정정/취소 이력을 저장합니다.

| 컬럼명                     | 데이터 타입    | 설명          | Null 허용 | PK / FK |
|-------------------------|-----------|-------------|---------|---------|
| modification_history_id | BIGINT    | 주문 변경 이력 ID | NO      | PK      |
| stock_order_id          | BIGINT    | 주문 ID       | NO      | FK      |
| modification_type       | ENUM      | 변경 유형       | NO      | -       |
| before_payload          | JSON      | 변경 전 데이터    | YES     | -       |
| after_payload           | JSON      | 변경 후 데이터    | YES     | -       |
| modified_by             | ENUM      | 변경 주체       | NO      | -       |
| modified_at             | TIMESTAMP | 변경 시각       | NO      | -       |

### modification_type

| 값      | 설명    |
|--------|-------|
| MODIFY | 주문 정정 |
| CANCEL | 주문 취소 |

### modified_by

| 값    | 설명       |
|------|----------|
| USER | 사용자      |
| AI   | AI 자동 변경 |

---

# 설계 특징

- 주문(Order)과 체결(Execution) 분리 구조 사용
- 주문 정정/취소 이력 별도 저장
- 포트폴리오 Snapshot 기반 이력 관리
- 금융 거래 데이터 immutable 기반 관리
- AI 자동 주문 지원
- 종목 마스터 기반 FK 참조 구조 사용
