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

---

## BANK-ACCOUNT-006. 계좌 유효성 검증

**POST** `/accounts/validate`

> transaction-server가 이체 실행 전 입금 대상 계좌의 존재 여부와 활성 상태를 검증하는 API
> X-User-Id 불필요 — 입금 대상 계좌 조회이므로 소유권 검증 없음

### Request Body

```json
{
  "toBankCode": "088",
  "toAccountNumber": "110-111-000074"
}
```

| 필드            | 타입   | 필수 | 설명        |
| --------------- | ------ | ---- | ----------- |
| toBankCode      | String | O    | 입금 은행 코드  |
| toAccountNumber | String | O    | 입금 계좌번호   |

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

| 상황            | 코드        | 메시지                       |
| --------------- | ----------- | ---------------------------- |
| 계좌 없음       | ACCOUNT_001 | 계좌가 존재하지 않습니다     |
| LOCKED / CLOSED / DORMANT | ACCOUNT_003 | 비활성 계좌입니다 |

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
> **멱등 보장:** 이미 SUCCESS 상태인 경우 재처리 없이 SUCCESS 응답 반환 (Saga orchestrator 재시도 안전)

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

---

## BANK-TRANSFER-004. 이체 취소

**POST** `/transfers/{transferId}/cancel`

> Saga 보상 트랜잭션 API
> Saga 실패 시 approve 이전 상태(REQUESTED / PROCESSING)의 Transfer를 명시적으로 CANCELLED로 전이
> 실제 잔액 변동 없음 — 상태 전이만 수행
> **멱등 보장:** 이미 CANCELLED 상태인 경우 재처리 없이 CANCELLED 응답 반환 (Saga orchestrator 재시도 안전)

### 취소 가능 상태

| 현재 상태   | 결과          | 비고                                                    |
| ----------- | ------------- | ------------------------------------------------------- |
| REQUESTED   | CANCELLED     | 취소 가능                                               |
| PROCESSING  | CANCELLED     | 취소 가능 (approve 이전이므로 잔액 변동 없음)           |
| CANCELLED   | CANCELLED     | 멱등 응답 반환 (Saga orchestrator 타임아웃 재시도 안전) |
| SUCCESS     | 예외 반환     | TRANSFER_003                                            |
| FAILED      | 예외 반환     | TRANSFER_003                                            |

### Request Body

없음

### Response `200 OK`

```json
{
  "success": true,
  "data": {
    "transferId": 5001,
    "transferStatus": "CANCELLED",
    "cancelledAt": "2026-05-18T10:30:10"
  },
  "meta": {
    "traceId": "uuid"
  }
}
```

### Error Cases

| 상황                                      | 코드         | 메시지                          |
| ----------------------------------------- | ------------ | ------------------------------- |
| 이체 건 없음                              | TRANSFER_001 | 해당 이체 건을 찾을 수 없습니다 |
| 접근 불가                                 | TRANSFER_004 | 본인 이체 건이 아닙니다         |
| 취소 불가 상태 (SUCCESS / FAILED / CANCELLED) | TRANSFER_003 | 이미 처리 완료된 이체입니다     |

