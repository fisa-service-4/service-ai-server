# transaction-server API 명세

> **Base URL:** `/baas/v1`
> **Port:** 8083
> **사용 구간:** 외부 서비스 <-> Transaction Server

---

# 공통 규칙

## HTTP Method 표기 규칙

```md
**GET** `/path`
**POST** `/path`
**PATCH** `/path`
**DELETE** `/path`
```

---

## 도메인 네이밍 규칙

```text
/bank
/stock
/total
```

---

## Query Parameter Naming 규칙

| 목적        | 이름      |
| ----------- | --------- |
| 시작일      | fromDate  |
| 종료일      | toDate    |
| 최소 금액   | minAmount |
| 최대 금액   | maxAmount |
| 페이지      | page      |
| 페이지 크기 | size      |

---

## Pagination Response 규칙

```json
{
  "success": true,
  "data": {
    "content": [],
    "page": 0,
    "size": 20,
    "totalElements": 100,
    "totalPages": 5
  },
  "meta": {
    "traceId": "uuid"
  }
}
```

---

## Response Wrapper 규칙

### 목록 응답

```json
{
  "success": true,
  "data": {
    "content": []
  },
  "meta": {
    "traceId": "uuid"
  }
}
```

### 단건 응답

```json
{
  "success": true,
  "data": {},
  "meta": {
    "traceId": "uuid"
  }
}
```

---

## 공통 헤더

| 헤더            | 설명   | 필수               |
| --------------- | ------ | ------------------ |
| Idempotency-Key | {uuid} | 이체/주문 API 전용 |

---

## 공통 응답 포맷

### 성공

```json
{
  "success": true,
  "data": {},
  "meta": {
    "traceId": "uuid"
  }
}
```

### 실패

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "에러 메시지"
  },
  "meta": {
    "traceId": "uuid"
  }
}
```

---

# BANK API

---

## BANK-ACCOUNT-001. 계좌 조회

**GET** `/bank/accounts`

### Query Parameters

| 이름   | 타입   | 필수 | 설명                               |
| ------ | ------ | ---- | ---------------------------------- |
| status | String | X    | ACTIVE / DORMANT / LOCKED / CLOSED |

### Response `200 OK`

```json id="vk9q0m"
{
  "success": true,
  "data": {
    "content": [
      {
        "accountId": 1001,
        "userId": 501,
        "bankCode": "088",
        "accountNumber": "110-123-456789",
        "accountName": "내 급여통장",
        "balance": 3500000,
        "accountStatus": "ACTIVE"
      }
    ]
  },
  "meta": {
    "traceId": "uuid"
  }
}
```

---

## BANK-ACCOUNT-002. 계좌 상세 조회

**GET** `/bank/accounts/{accountId}`

### Response `200 OK`

```json id="dl7jkn"
{
  "success": true,
  "data": {
    "accountId": 1001,
    "userId": 501,
    "bankCode": "088",
    "accountNumber": "110-123-456789",
    "accountName": "내 급여통장",
    "balance": 3500000,
    "accountStatus": "ACTIVE",
    "openedAt": "2024-01-15T09:00:00",
    "closedAt": null,
    "updatedAt": "2026-05-17T14:22:00"
  },
  "meta": {
    "traceId": "uuid"
  }
}
```

## BANK-ACCOUNT-003. 계좌 잔액 조회

**GET** `/accounts/{accountId}/balance`

### Response `200 OK`

```json id="vr3zgd"
{
  "success": true,
  "data": {
    "accountId": 1001,
    "balance": 3500000,
    "updatedAt": "2026-05-18T10:15:00"
  },
  "meta": {
    "traceId": "uuid"
  }
}
```

---

## BANK-ACCOUNT-004. 거래내역 조회

**GET** `/accounts/{accountId}/transactions`

### Query Parameters

| 이름      | 타입    | 필수 | 설명                                                            |
| --------- | ------- | ---- | --------------------------------------------------------------- |
| type      | String  | X    | DEPOSIT / WITHDRAW / TRANSFER_IN / TRANSFER_OUT / AUTO_TRANSFER |
| channel   | String  | X    | APP / AI_AGENT                                                  |
| status    | String  | X    | SUCCESS / FAILED / CANCELLED                                    |
| fromDate  | Date    | X    | 조회 시작일 (YYYY-MM-DD)                                        |
| toDate    | Date    | X    | 조회 종료일 (YYYY-MM-DD)                                        |
| minAmount | Decimal | X    | 최소 거래 금액                                                  |
| maxAmount | Decimal | X    | 최대 거래 금액                                                  |
| page      | Integer | X    | 페이지 번호 (기본값: 0)                                         |
| size      | Integer | X    | 페이지 크기 (기본값: 20)                                        |

### Response `200 OK`

```json id="0h2drx"
{
  "success": true,
  "data": {
    "content": [
      {
        "transactionId": 9001,
        "transactionType": "DEPOSIT",
        "transactionCategory": "급여",
        "amount": 3000000,
        "balanceAfter": 3500000,
        "transactionChannel": "APP",
        "transactionStatus": "SUCCESS",
        "transactionAt": "2026-05-01T09:00:00"
      }
    ],
    "page": 0,
    "size": 20,
    "totalElements": 42,
    "totalPages": 3
  },
  "meta": {
    "traceId": "uuid"
  }
}
```

---

## BANK-ACCOUNT-005. 거래 카테고리 조회

**GET** `/accounts/{accountId}/transactions/categories`

### Query Parameters

| 이름     | 타입 | 필수 | 설명                     |
| -------- | ---- | ---- | ------------------------ |
| fromDate | Date | O    | 집계 시작일 (YYYY-MM-DD) |
| toDate   | Date | O    | 집계 종료일 (YYYY-MM-DD) |

### Response `200 OK`

```json id="xq9yqv"
{
  "success": true,
  "data": {
    "categories": [
      {
        "category": "급여",
        "totalAmount": 3000000,
        "count": 1
      },
      {
        "category": "식비",
        "totalAmount": 280000,
        "count": 12
      },
      {
        "category": "교통",
        "totalAmount": 95000,
        "count": 8
      }
    ]
  },
  "meta": {
    "traceId": "uuid"
  }
}
```

## BANK-TRANSFER-001. 이체 실행

**POST** `/bank/transfers`

> Write API
> Idempotency-Key 필수

### Request Body

```json
{
  "fromAccountId": 1001,
  "toBankCode": "020",
  "toAccountNumber": "301-0987-1234",
  "transferAmount": 500000,
  "requestedBy": "USER"
}
```

| 필드            | 타입    | 필수 | 설명               |
| --------------- | ------- | ---- | ------------------ |
| fromAccountId   | Long    | O    | 출금 계좌 ID       |
| toBankCode      | String  | O    | 입금 은행 코드     |
| toAccountNumber | String  | O    | 입금 계좌번호      |
| transferAmount  | Decimal | O    | 이체 금액 (0 초과) |
| requestedBy     | String  | O    | USER / AI          |

### Response `201 Created`

```json
{
  "success": true,
  "data": {
    "transferId": 5001,
    "transferStatus": "REQUESTED",
    "requestedAt": "2026-05-18T10:30:00"
  },
  "meta": {
    "traceId": "uuid"
  }
}
```

### Error Cases

| 상황           | 코드         | 메시지                        |
| -------------- | ------------ | ----------------------------- |
| 잔액 부족      | TRANSFER_002 | 잔액이 부족합니다             |
| 계좌 이상 상태 | ACCOUNT_003  | 계좌 상태가 유효하지 않습니다 |
| 접근 불가      | ACCOUNT_002  | 본인 계좌가 아닙니다          |

---

## BANK-TRANSFER-002. 이체 승인

**POST** `/bank/transfers/{transferId}/approve`

> Saga 기반 분산 트랜잭션 Commit 단계 수행 API
> 출금/입금 반영 및 최종 상태 확정 처리

### Response `200 OK`

```json
{
  "success": true,
  "data": {
    "transferId": 5001,
    "transferStatus": "SUCCESS",
    "completedAt": "2026-05-18T10:30:05"
  },
  "meta": {
    "traceId": "uuid"
  }
}
```

### Error Cases

| 상황         | 코드         | 메시지                          |
| ------------ | ------------ | ------------------------------- |
| 이체 건 없음 | TRANSFER_001 | 해당 이체 건을 찾을 수 없습니다 |
| 중복 승인    | TRANSFER_003 | 이미 처리 완료된 이체입니다     |

---

## BANK-TRANSFER-003. 이체 결과 조회

**GET** `/bank/transfers/{transferId}`

### Response `200 OK`

```json
{
  "success": true,
  "data": {
    "transferId": 5001,
    "fromAccountId": 1001,
    "toBankCode": "020",
    "toAccountNumber": "301-0987-1234",
    "transferAmount": 500000,
    "transferStatus": "SUCCESS",
    "failureReason": null,
    "requestedAt": "2026-05-18T10:30:00",
    "completedAt": "2026-05-18T10:30:05"
  },
  "meta": {
    "traceId": "uuid"
  }
}
```

### Error Cases

| 상황         | 코드         | 메시지                          |
| ------------ | ------------ | ------------------------------- |
| 이체 건 없음 | TRANSFER_001 | 해당 이체 건을 찾을 수 없습니다 |
| 접근 불가    | TRANSFER_004 | 본인 이체 건이 아닙니다         |

---

# STOCK API

---

## STOCK-SEARCH-001. 종목 검색

**GET** `/stock/search`

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

**GET** `/stock/{stockCode}/price`

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

**GET** `/stock/{stockCode}/charts`

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

**GET** `/stock/accounts`

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
        "bankCode": "039"
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

**GET** `/stock/accounts/{accountId}/cash-balance`

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

## STOCK-ORDER-001. 주문 생성

**POST** `/stock/accounts/{accountId}/orders`

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

| 필드        | 타입    | 필수 | 설명                                      |
| ----------- | ------- | ---- | ----------------------------------------- |
| stockCode   | String  | O    | 종목 코드                                 |
| orderType   | String  | O    | BUY / SELL                                |
| orderMethod | String  | O    | MARKET / LIMIT                            |
| quantity    | Integer | O    | 주문 수량                                 |
| price       | Integer | X    | 주문 가격 (LIMIT 시 필수, MARKET 시 null) |

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

### Error Cases

| 상황                | 코드      | 메시지                      |
| ------------------- | --------- | --------------------------- |
| 주문 가능 금액 부족 | ORDER_001 | 주문 가능 금액이 부족합니다 |
| 보유 수량 부족      | ORDER_002 | 보유 수량이 부족합니다      |

---

## STOCK-ORDER-002. 주문 취소

**POST** `/stock/orders/{orderId}/cancel`

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

## STOCK-ORDER-003. 주문 조회

**GET** `/stock/accounts/{accountId}/orders`

### Query Parameters

| 이름      | 타입    | 필수 | 설명                                                     |
| --------- | ------- | ---- | -------------------------------------------------------- |
| status    | String  | X    | REQUESTED / PARTIAL_FILLED / FILLED / CANCELLED / FAILED |
| orderType | String  | X    | BUY / SELL                                               |
| page      | Integer | X    | 페이지 번호 (기본값: 0)                                  |
| size      | Integer | X    | 페이지 크기 (기본값: 20)                                 |

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

## STOCK-ORDER-004. 주문 상세 조회

**GET** `/stock/orders/{orderId}`

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

## STOCK-EXECUTION-001. 체결 조회

**GET** `/stock/accounts/{accountId}/executions`

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

## STOCK-RETURN-001. 수익률 조회

**GET** `/stock/accounts/{accountId}/returns`

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

## STOCK-HOLDING-001. 보유 종목 조회

**GET** `/stock/accounts/{accountId}/holdings`

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

# COMMON API

---

## TOTAL-001. 포트폴리오 조회

**GET** `/total/portfolio`

### Query Parameters

| 이름      | 타입 | 필수 | 설명         |
| --------- | ---- | ---- | ------------ |
| accountId | Long | O    | 증권 계좌 ID |

### Response `200 OK`

```json
{
  "success": true,
  "data": {
    "totalAsset": 25000000,
    "cashAsset": 8000000,
    "stockAsset": 15000000,
    "savingAsset": 2000000,
    "availableCash": 3000000,
    "assetRatio": {
      "cash": 32,
      "stock": 60,
      "saving": 8
    }
  },
  "meta": {
    "traceId": "uuid"
  }
}
```
