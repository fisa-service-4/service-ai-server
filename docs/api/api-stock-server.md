# stock-server API 명세

> **Base URL:** `/internal/v1/stock`
> **Port:** 8082
> **사용 구간:** Transaction Server ↔ 내부 Stock-Server

---

## 공통 헤더

| 헤더       | 설명           | 필수 |
| ---------- | -------------- | ---- |
| X-User-Id  | 사용자 식별 ID | O    |
| X-Trace-Id | 요청 추적 ID   | O    |

> JWT 인증 없음.
> 내부 서버 간 통신 전용이며 Core 서버는 검증 완료된 내부 요청만 처리

---

## 공통 응답 헤더

| 헤더       | 설명         | 필수 |
| ---------- | ------------ | ---- |
| X-Trace-Id | 요청 추적 ID | O    |

> Response의 X-Trace-Id는 Request의 X-Trace-Id와 동일 값 사용

---

## COMMON-002. 헬스 체크 (Stock)

**GET** `/health`

### Response `200 OK`

```json
{
  "success": true,
  "data": {
    "database": "UP",
    "server": "UP"
  },
  "meta": {
    "traceId": "uuid"
  }
}
```

## RECONCILIATION-002. 정합성 검증 결과 조회

**GET** `/reconciliation/result`

### Query Parameters

| 이름             | 타입 | 필수 | 설명                     |
| ---------------- | ---- | ---- | ------------------------ |
| reconciliationId | Long | X    | 검증 ID (미입력 시 최신) |

### Response `200 OK`

```json
{
  "success": true,
  "data": {
    "reconciliationId": 101,
    "status": "SUCCESS",
    "totalChecked": 1500,
    "mismatchCount": 2,
    "mismatches": [
      {
        "entityType": "TRANSFER",
        "entityId": 5001,
        "reason": "balance mismatch"
      }
    ],
    "executedAt": "2026-05-17T03:00:00"
  },
  "meta": {
    "traceId": "uuid"
  }
}
```

---

# STOCK API

---

## STOCK-SEARCH-001. 종목 검색

**GET** `/search`

### Query Parameters

| 이름    | 타입   | 필수 | 설명                 |
| ------- | ------ | ---- | -------------------- |
| keyword | String | O    | 종목명 또는 종목코드 |

### Response `200 OK`

```json
{
  "success": true,
  "data": {
    "content": [
      {
        "stockCode": "005930",
        "stockName": "삼성전자",
        "market": "KOSPI",
        "currentPrice": 82000,
        "changeRate": -1.2
      }
    ]
  },
  "meta": {
    "traceId": "uuid"
  }
}
```

---

## STOCK-PRICE-001. 현재가 조회

**GET** `/{stockCode}/price`

### Response `200 OK`

```json
{
  "success": true,
  "data": {
    "stockCode": "005930",
    "stockName": "삼성전자",
    "currentPrice": 82000,
    "changeRate": -1.2,
    "updatedAt": "2026-05-17T12:00:00"
  },
  "meta": {
    "traceId": "uuid"
  }
}
```

---

## STOCK-CHART-001. 차트 조회

**GET** `/{stockCode}/charts`

### Query Parameters

| 이름     | 타입   | 필수 | 설명                     |
| -------- | ------ | ---- | ------------------------ |
| interval | String | O    | DAILY / WEEKLY / MONTHLY |
| fromDate | Date   | X    | 조회 시작일 (YYYY-MM-DD) |
| toDate   | Date   | X    | 조회 종료일 (YYYY-MM-DD) |

### Response `200 OK`

```json
{
  "success": true,
  "data": {
    "content": [
      {
        "date": "2026-05-17",
        "open": 81000,
        "high": 82500,
        "low": 80500,
        "close": 82000,
        "volume": 12345678
      }
    ]
  },
  "meta": {
    "traceId": "uuid"
  }
}
```

---

## STOCK-ACCOUNT-001. 주문 가능 계좌 조회

**GET** `/accounts`

### Response `200 OK`

```json
{
  "success": true,
  "data": {
    "content": [
      {
        "accountId": 2001,
        "accountNumber": "300-123-456789",
        "accountName": "내 주식 계좌",
        "bankCode": "243"
      }
    ]
  },
  "meta": {
    "traceId": "uuid"
  }
}
```

---

## STOCK-ACCOUNT-002. 예수금 조회

**GET** `/accounts/{accountId}/cash-balance`

### Response `200 OK`

```json
{
  "success": true,
  "data": {
    "accountId": 2001,
    "cashBalance": 3000000,
    "availableBalance": 2800000
  },
  "meta": {
    "traceId": "uuid"
  }
}
```

---

## STOCK-ACCOUNT-003. 계좌 유효성 검증

**POST** `/accounts/validate`

> **온프레미스 내부 전용 API** — transaction-server → stock-server 직접 호출.
> 외부 클라이언트(service-backend, 프론트엔드) 호출 대상 아님.
> 이체 Saga 진행 전 입금 대상 증권 계좌의 존재 여부 및 상태를 검증합니다.

### Request Body

```json
{
  "toBankCode": "243",
  "toAccountNumber": "300-777-000071"
}
```

### Request Fields

| 필드            | 타입   | 필수 | 설명                                                        |
| --------------- | ------ | ---- | ----------------------------------------------------------- |
| toBankCode      | String | O    | 증권사 식별 코드. `243` (한국투자증권) / `247` (NH투자증권) |
| toAccountNumber | String | O    | 계좌번호                                                    |

### Response `200 OK`

```json
{
  "success": true,
  "data": {
    "validYn": true,
    "status": "ACTIVE"
  },
  "meta": {
    "traceId": "uuid"
  }
}
```

### Error Cases

| 상황            | 코드        | HTTP | 메시지                    |
| --------------- | ----------- | ---- | ------------------------- |
| 계좌 없음       | ACCOUNT_001 | 404  | 계좌를 찾을 수 없습니다   |
| LOCKED / CLOSED | ACCOUNT_003 | 400  | 사용할 수 없는 계좌입니다 |

---

## STOCK-ORDER-001. 주문 생성

**POST** `/accounts/{accountId}/orders`

> Write API
> Idempotency-Key 필수

### Request Body

```json
{
  "stockCode": "005930",
  "orderType": "BUY",
  "orderMethod": "LIMIT",
  "quantity": 10,
  "price": 82000
}
```

### Request Fields

| 필드        | 타입    | 필수 | 설명               |
| ----------- | ------- | ---- | ------------------ |
| stockCode   | String  | O    | 종목 코드          |
| orderType   | String  | O    | BUY / SELL         |
| orderMethod | String  | O    | MARKET / LIMIT     |
| quantity    | Integer | O    | 주문 수량          |
| price       | Integer | X    | LIMIT 주문 시 필수 |

### Response `201 Created`

```json
{
  "success": true,
  "data": {
    "orderId": 1001,
    "stockCode": "005930",
    "orderType": "BUY",
    "orderMethod": "LIMIT",
    "quantity": 10,
    "price": 82000,
    "filledQuantity": 0,
    "remainingQuantity": 10,
    "status": "REQUESTED",
    "orderedAt": "2026-05-17T12:00:00"
  },
  "meta": {
    "traceId": "uuid"
  }
}
```

---

## STOCK-ORDER-002. 주문 조회

**GET** `/accounts/{accountId}/orders`

### Query Parameters

| 이름      | 타입    | 필수 | 설명                                                                          |
| --------- | ------- | ---- | ----------------------------------------------------------------------------- |
| status    | String  | X    | REQUESTED / PARTIAL_FILLED / FILLED / CANCELLED / FAILED / REJECTED / EXPIRED |
| orderType | String  | X    | BUY / SELL                                                                    |
| page      | Integer | X    | 페이지 번호 (기본값: 0)                                                       |
| size      | Integer | X    | 페이지 크기 (기본값: 20)                                                      |

### Response `200 OK`

```json
{
  "success": true,
  "data": {
    "content": [
      {
        "orderId": 1001,
        "stockCode": "005930",
        "stockName": "삼성전자",
        "orderType": "BUY",
        "orderMethod": "LIMIT",
        "quantity": 10,
        "filledQuantity": 7,
        "remainingQuantity": 3,
        "price": 82000,
        "status": "PARTIAL_FILLED",
        "orderedAt": "2026-05-17T12:00:00"
      }
    ],
    "page": 0,
    "size": 20,
    "totalElements": 1,
    "totalPages": 1
  },
  "meta": {
    "traceId": "uuid"
  }
}
```

---

## STOCK-ORDER-003. 주문 상세 조회

**GET** `/orders/{orderId}`

### Response `200 OK`

```json
{
  "success": true,
  "data": {
    "orderId": 1001,
    "accountId": 2001,
    "stockCode": "005930",
    "stockName": "삼성전자",
    "orderType": "BUY",
    "orderMethod": "LIMIT",
    "quantity": 10,
    "filledQuantity": 7,
    "remainingQuantity": 3,
    "price": 82000,
    "averageExecutionPrice": 81950,
    "status": "PARTIAL_FILLED",
    "orderedAt": "2026-05-17T12:00:00",
    "updatedAt": "2026-05-17T12:03:00"
  },
  "meta": {
    "traceId": "uuid"
  }
}
```

---

## STOCK-ORDER-004. 주문 취소

**POST** `/orders/{orderId}/cancel`

> Write API
> Idempotency-Key 필수

### Response `200 OK`

```json
{
  "success": true,
  "data": {
    "orderId": 1001,
    "status": "CANCELLED",
    "cancelledQuantity": 8,
    "filledQuantity": 2,
    "remainingQuantity": 0,
    "cancelledAt": "2026-05-17T12:10:00"
  },
  "meta": {
    "traceId": "uuid"
  }
}
```

---

## STOCK-EXECUTION-001. 체결 조회

**GET** `/accounts/{accountId}/executions`

### Query Parameters

| 이름      | 타입    | 필수 | 설명                     |
| --------- | ------- | ---- | ------------------------ |
| stockCode | String  | X    | 종목 코드                |
| fromDate  | Date    | X    | 조회 시작일 (YYYY-MM-DD) |
| toDate    | Date    | X    | 조회 종료일 (YYYY-MM-DD) |
| page      | Integer | X    | 페이지 번호 (기본값: 0)  |
| size      | Integer | X    | 페이지 크기 (기본값: 20) |

### Response `200 OK`

```json
{
  "success": true,
  "data": {
    "content": [
      {
        "executionId": 501,
        "orderId": 1001,
        "stockCode": "005930",
        "stockName": "삼성전자",
        "executedPrice": 82000,
        "executedQuantity": 5,
        "executionAmount": 410000,
        "executedAt": "2026-05-17T12:01:00"
      }
    ],
    "page": 0,
    "size": 20,
    "totalElements": 1,
    "totalPages": 1
  },
  "meta": {
    "traceId": "uuid"
  }
}
```

---

## STOCK-HOLDING-001. 보유 종목 조회

**GET** `/accounts/{accountId}/holdings`

### Response `200 OK`

```json
{
  "success": true,
  "data": {
    "content": [
      {
        "stockCode": "005930",
        "stockName": "삼성전자",
        "quantity": 20,
        "averagePrice": 78000,
        "currentPrice": 82000,
        "evaluationAmount": 1640000,
        "unrealizedProfit": 80000,
        "profitRate": 5.12
      }
    ]
  },
  "meta": {
    "traceId": "uuid"
  }
}
```

---

## STOCK-RETURN-001. 수익률 조회

**GET** `/accounts/{accountId}/returns`

### Response `200 OK`

```json
{
  "success": true,
  "data": {
    "accountId": 2001,
    "dailyReturnRate": 1.5,
    "monthlyReturnRate": 7.3,
    "yearlyReturnRate": 18.1
  },
  "meta": {
    "traceId": "uuid"
  }
}
```

---

---

# ====== transaction-saga용 API ======

> transaction-server → stock-server 인바운드 호출 전용.
> Saga orchestration 연동용이며 일반 클라이언트 호출 대상 아님.

---

## STOCK-CASH-001. 예수금 입금

**POST** `/accounts/{accountId}/cash/deposit`

> Write API — Saga 정상 step

### Request Body

```json
{
  "amount": 500000,
  "sagaId": 1001
}
```

### Request Fields

| 필드   | 타입    | 필수 | 설명                  |
| ------ | ------- | ---- | --------------------- |
| amount | Decimal | O    | 입금 금액 (0 초과)    |
| sagaId | Long    | X    | Saga 추적 ID (로깅용) |

### Response `200 OK`

```json
{
  "success": true,
  "data": {
    "accountId": 2001,
    "cashBalance": 10500000
  },
  "meta": {
    "traceId": "uuid"
  }
}
```

### Error Cases

| 상황           | 코드        | 메시지                       |
| -------------- | ----------- | ---------------------------- |
| 계좌 없음      | ACCOUNT_001 | 해당 계좌를 찾을 수 없습니다 |
| 본인 계좌 아님 | ACCOUNT_002 | 본인 계좌가 아닙니다         |

---

## STOCK-CASH-002. 예수금 출금

**POST** `/accounts/{accountId}/cash/withdraw`

> Write API — Saga compensation step (rollback용)

### Request Body

```json
{
  "amount": 500000,
  "sagaId": 1001
}
```

### Request Fields

| 필드   | 타입    | 필수 | 설명                  |
| ------ | ------- | ---- | --------------------- |
| amount | Decimal | O    | 출금 금액 (0 초과)    |
| sagaId | Long    | X    | Saga 추적 ID (로깅용) |

### Response `200 OK`

```json
{
  "success": true,
  "data": {
    "accountId": 2001,
    "cashBalance": 10000000
  },
  "meta": {
    "traceId": "uuid"
  }
}
```

### Error Cases

| 상황           | 코드         | 메시지                       |
| -------------- | ------------ | ---------------------------- |
| 계좌 없음      | ACCOUNT_001  | 해당 계좌를 찾을 수 없습니다 |
| 본인 계좌 아님 | ACCOUNT_002  | 본인 계좌가 아닙니다         |
| 잔액 부족      | TRANSFER_002 | 잔액이 부족합니다            |
