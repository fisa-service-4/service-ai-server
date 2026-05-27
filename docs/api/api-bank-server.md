# bank-server API 명세

> **Base URL:** `/internal/v1/bank`
> **Port:** 8081
> **사용 구간:** Transaction Server <-> 내부 Bank 서버

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

# 공통 API

---

## COMMON-001. 헬스 체크 (Bank)

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

---

## RECONCILIATION-001. 정합성 검증 실행

**POST** `/reconciliation/run`

### Request Body

```json
{
  "targetDate": "2026-05-17"
}
```

| 필드       | 타입 | 필수 | 설명                            |
| ---------- | ---- | ---- | ------------------------------- |
| targetDate | Date | X    | 검증 대상 날짜 (미입력 시 전일) |

### Response `202 Accepted`

```json
{
  "success": true,
  "data": {
    "reconciliationId": 101,
    "status": "STARTED"
  },
  "meta": {
    "traceId": "uuid"
  }
}
```

---

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

# BANK API

---

## BANK-ACCOUNT-001. 계좌 조회

**GET** `/accounts`

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

**GET** `/accounts/{accountId}`

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

---

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

| 이름     | 타입    | 필수 | 설명                     |
| -------- | ------- | ---- | ------------------------ |
| fromDate | Date    | X    | 조회 시작일 (YYYY-MM-DD) |
| toDate   | Date    | X    | 조회 종료일 (YYYY-MM-DD) |
| page     | Integer | X    | 페이지 번호 (기본값: 0)  |
| size     | Integer | X    | 페이지 크기 (기본값: 20) |

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

## BANK-ACCOUNT-005. 거래 필터 조회

**GET** `/accounts/{accountId}/transactions/filter`

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

```json id="s0yjf6"
{
  "success": true,
  "data": {
    "content": [
      {
        "transactionId": 9005,
        "transactionType": "WITHDRAW",
        "transactionCategory": "식비",
        "amount": 50000,
        "balanceAfter": 3450000,
        "transactionChannel": "APP",
        "transactionStatus": "SUCCESS",
        "transactionAt": "2026-05-10T13:22:00"
      }
    ],
    "page": 0,
    "size": 20,
    "totalElements": 5,
    "totalPages": 1
  },
  "meta": {
    "traceId": "uuid"
  }
}
```

---

## BANK-ACCOUNT-006. 거래 카테고리 조회

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

---

## BANK-TRANSFER-001. 이체 실행

**POST** `/transfers`

> Write API
> Idempotency-Key 필수

### Request Body

```json id="e4sxt6"
{
  "fromAccountId": 1001,
  "toBankCode": "020",
  "toAccountNumber": "301-0987-1234",
  "transferAmount": 500000,
  "requestedBy": "USER"
}
```

### Response `201 Created`

```json id="l3znk6"
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

---

## BANK-TRANSFER-002. 이체 상태 조회

**GET** `/transfers/{transferId}`

> Saga 기반 이체 상태 조회 API
> Transfer 진행 상태 및 결과 조회

### Response `200 OK`

```json id="0t7w20"
{
  "success": true,
  "data": {
    "transferId": 5001,
    "transferStatus": "PROCESSING",
    "fromAccountId": 1001,
    "toBankCode": "020",
    "toAccountNumber": "301-0987-1234",
    "transferAmount": 500000,
    "requestedAt": "2026-05-18T10:30:00",
    "completedAt": null
  },
  "meta": {
    "traceId": "uuid"
  }
}
```

---

## BANK-TRANSFER-003. 이체 승인

**POST** `/transfers/{transferId}/approve`

> Saga 기반 분산 트랜잭션 Commit 단계 수행 API
> 출금/입금 반영 및 최종 상태 확정 처리

### Response `200 OK`

```json id="0t7w20"
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
