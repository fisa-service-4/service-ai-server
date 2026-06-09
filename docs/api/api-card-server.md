# card-server API 명세

> **Base URL:** `/internal/v1/card`
> **Port:** 8081
> **사용 구간:** Transaction Server → Bank Server (Card 도메인)

---

## 공통 헤더

| 헤더       | 설명           | 필수                    |
| ---------- | -------------- | ----------------------- |
| X-User-Id  | 사용자 식별 ID | O (카드 소유자 식별용)   |
| X-Trace-Id | 요청 추적 ID   | O                       |

> JWT 인증 없음.
> 내부 서버 간 통신 전용이며 Bank Server는 검증 완료된 내부 요청만 처리

---

## 공통 응답 헤더

| 헤더       | 설명         |
| ---------- | ------------ |
| X-Trace-Id | 요청 추적 ID |

> Response의 X-Trace-Id는 Request의 X-Trace-Id와 동일 값 사용

---

## 에러 코드

| 코드         | HTTP | 설명                                    |
| ------------ | ---- | --------------------------------------- |
| CARD_001     | 404  | 카드를 찾을 수 없음                      |
| CARD_002     | 403  | 본인 카드가 아닙니다                     |
| CARD_003     | 404  | 카드 승인 내역을 찾을 수 없음            |
| TRANSFER_002 | 400  | 잔액이 부족합니다 (결제 시)              |
| ACCOUNT_001  | 404  | 계좌를 찾을 수 없음 (결제 시)            |
| ACCOUNT_003  | 400  | 계좌 상태가 유효하지 않음 (결제 시)      |

---

# CARD API

---

## CARD-001. 사용자 카드 목록 조회

**GET** `/cards`

> X-User-Id 헤더로 사용자를 식별하여 해당 사용자의 카드 목록을 반환한다.

### Response `200 OK`

```json
{
  "success": true,
  "data": {
    "content": [
      {
        "cardId": 1,
        "cardNumber": "1234-****-****-5678",
        "linkedAccountId": 1001,
        "cardStatus": "ACTIVE"
      }
    ]
  },
  "meta": {
    "traceId": "uuid"
  }
}
```

| 필드            | 타입   | 설명                                         |
| --------------- | ------ | -------------------------------------------- |
| cardId          | Long   | 카드 ID                                      |
| cardNumber      | String | 마스킹된 카드 번호 (뒤 4자리 노출)            |
| linkedAccountId | Long   | 연결 계좌 ID (nullable)                      |
| cardStatus      | String | ACTIVE / LOST / EXPIRED / SUSPENDED / CLOSED |

---

## CARD-002. 카드 상세 조회

**GET** `/cards/{cardId}`

### Path Variable

| 이름   | 타입 | 설명    |
| ------ | ---- | ------- |
| cardId | Long | 카드 ID |

### Response `200 OK`

```json
{
  "success": true,
  "data": {
    "cardId": 1,
    "userId": 501,
    "cardNumber": "1234-****-****-5678",
    "linkedAccountId": 1001,
    "cardStatus": "ACTIVE"
  },
  "meta": {
    "traceId": "uuid"
  }
}
```

### Error Cases

| 상황           | 코드     | 메시지                  |
| -------------- | -------- | ----------------------- |
| 카드 없음      | CARD_001 | 카드를 찾을 수 없습니다 |
| 본인 카드 아님 | CARD_002 | 본인 카드가 아닙니다    |

---

## CARD-003. 카드 승인 내역 조회

**GET** `/cards/{cardId}/approvals`

> 기간 조회 및 페이지네이션을 지원한다.

### Path Variable

| 이름   | 타입 | 설명    |
| ------ | ---- | ------- |
| cardId | Long | 카드 ID |

### Query Parameters

| 이름             | 타입    | 필수 | 설명                                                                                                                                   |
| ---------------- | ------- | ---- | -------------------------------------------------------------------------------------------------------------------------------------- |
| fromDate         | Date    | X    | 조회 시작일 (YYYY-MM-DD)                                                                                                               |
| toDate           | Date    | X    | 조회 종료일 (YYYY-MM-DD)                                                                                                               |
| approvalStatus   | String  | X    | APPROVED / DECLINED / CANCELLED                                                                                                        |
| merchantCategory | String  | X    | FOOD_BEVERAGE / CAFE / TRANSPORTATION / SHOPPING / MART / ENTERTAINMENT / MEDICAL / EDUCATION / SUBSCRIPTION / COMMUNICATION / BEAUTY / TRAVEL / GAS / ETC |
| page             | Integer | X    | 페이지 번호 (기본값: 0)                                                                                                                 |
| size             | Integer | X    | 페이지 크기 (기본값: 20)                                                                                                                |

### Response `200 OK`

```json
{
  "success": true,
  "data": {
    "content": [
      {
        "approvalId": 50,
        "accountTransactionId": 9001,
        "merchantName": "스타벅스 강남점",
        "merchantCategory": "CAFE",
        "approvalAmount": 5500,
        "approvalStatus": "APPROVED",
        "approvalCode": "ABC123",
        "approvedAt": "2026-05-17T12:00:00"
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

| 필드                 | 타입     | 설명                            |
| -------------------- | -------- | ------------------------------- |
| approvalId           | Long     | 승인 이력 ID                    |
| accountTransactionId | Long     | 연결된 은행 거래 ID (nullable)  |
| merchantName         | String   | 가맹점명                        |
| merchantCategory     | String   | 가맹점 카테고리 (nullable)      |
| approvalAmount       | Decimal  | 승인 금액                       |
| approvalStatus       | String   | APPROVED / DECLINED / CANCELLED |
| approvalCode         | String   | 승인 코드 (nullable)            |
| approvedAt           | DateTime | 승인 시각                       |

### Error Cases

| 상황           | 코드     | 메시지                  |
| -------------- | -------- | ----------------------- |
| 카드 없음      | CARD_001 | 카드를 찾을 수 없습니다 |
| 본인 카드 아님 | CARD_002 | 본인 카드가 아닙니다    |

---

## CARD-004. 카드 승인 상세 조회

**GET** `/card-approvals/{approvalId}`

### Path Variable

| 이름       | 타입 | 설명         |
| ---------- | ---- | ------------ |
| approvalId | Long | 카드 승인 ID |

### Response `200 OK`

```json
{
  "success": true,
  "data": {
    "approvalId": 50,
    "cardId": 1,
    "accountTransactionId": 9001,
    "merchantName": "스타벅스 강남점",
    "merchantCategory": "CAFE",
    "approvalAmount": 5500,
    "approvalStatus": "APPROVED",
    "approvalCode": "ABC123",
    "declinedReason": null,
    "approvedAt": "2026-05-17T12:00:00"
  },
  "meta": {
    "traceId": "uuid"
  }
}
```

| 필드                 | 타입     | 설명                                      |
| -------------------- | -------- | ----------------------------------------- |
| approvalId           | Long     | 승인 이력 ID                              |
| cardId               | Long     | 카드 ID                                   |
| accountTransactionId | Long     | 연결된 은행 거래 ID (nullable)            |
| merchantName         | String   | 가맹점명                                  |
| merchantCategory     | String   | 가맹점 카테고리 (nullable)                |
| approvalAmount       | Decimal  | 승인 금액                                 |
| approvalStatus       | String   | APPROVED / DECLINED / CANCELLED           |
| approvalCode         | String   | 승인 코드 (nullable)                      |
| declinedReason       | String   | 승인 거절 사유 (DECLINED인 경우에만 표시) |
| approvedAt           | DateTime | 승인 시각                                 |

### Error Cases

| 상황           | 코드     | 메시지                              |
| -------------- | -------- | ----------------------------------- |
| 승인 내역 없음 | CARD_003 | 카드 승인 내역을 찾을 수 없습니다   |
| 본인 카드 아님 | CARD_002 | 본인 카드가 아닙니다                |

---

## CARD-005. 계좌별 카드 목록 조회

**GET** `/accounts/{accountId}/cards`

> accountId로 연결된 카드 목록을 조회합니다.
> X-User-Id 불필요 — 계좌 ID로 카드를 특정하므로 소유권 검증 없음.
> mydata-server가 거래내역 조회 시 카드 승인내역 매핑을 위해 호출합니다.

### Path Variable

| 이름      | 타입 | 설명    |
| --------- | ---- | ------- |
| accountId | Long | 계좌 ID |

### Response `200 OK`

```json
{
  "success": true,
  "data": {
    "content": [
      {
        "cardId": 1,
        "cardNumber": "1234-****-****-5678",
        "linkedAccountId": 1001,
        "cardStatus": "ACTIVE"
      }
    ]
  },
  "meta": {
    "traceId": "uuid"
  }
}
```

| 필드            | 타입   | 설명                                         |
| --------------- | ------ | -------------------------------------------- |
| cardId          | Long   | 카드 ID                                      |
| cardNumber      | String | 마스킹된 카드 번호 (뒤 4자리 노출)            |
| linkedAccountId | Long   | 연결 계좌 ID                                 |
| cardStatus      | String | ACTIVE / LOST / EXPIRED / SUSPENDED / CLOSED |

---

## CARD-006. 카드 결제 처리

**POST** `/cards/{cardId}/payments`

> 카드 결제를 처리한다. 실제 PG / VAN 프로세스는 수행하지 않으나,
> 계좌 잔액 차감 및 원장 기록은 실제와 동일하게 처리한다.
>
> **처리 순서:**
> 1. 카드 및 연결 계좌(`linked_account_id`) 유효성 검증
> 2. 계좌 잔액 확인 (잔액 부족 시 실패)
> 3. Bank DB: `account_transaction` (transaction_type=PAYMENT) 레코드 생성 및 `account` 잔액 차감
> 4. Card DB: `card_approval` 레코드 생성 (APPROVED), `account_transaction_id` 연결, `merchant_category` 기록

### Path Variable

| 이름   | 타입 | 설명    |
| ------ | ---- | ------- |
| cardId | Long | 카드 ID |

### Request Body

```json
{
  "merchantName": "스타벅스 강남점",
  "merchantCategory": "CAFE",
  "approvalAmount": 5500
}
```

| 필드             | 타입    | 필수 | 설명                                                                                                                                           |
| ---------------- | ------- | ---- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| merchantName     | String  | O    | 가맹점명                                                                                                                                       |
| merchantCategory | String  | X    | FOOD_BEVERAGE / CAFE / TRANSPORTATION / SHOPPING / MART / ENTERTAINMENT / MEDICAL / EDUCATION / SUBSCRIPTION / COMMUNICATION / BEAUTY / TRAVEL / GAS / ETC |
| approvalAmount   | Decimal | O    | 결제 금액 (0 초과)                                                                                                                              |

### Response `201 Created`

```json
{
  "success": true,
  "data": {
    "approvalId": 50,
    "cardId": 1,
    "accountTransactionId": 9001,
    "merchantName": "스타벅스 강남점",
    "merchantCategory": "CAFE",
    "approvalAmount": 5500,
    "approvalStatus": "APPROVED",
    "balanceAfter": 994500,
    "approvedAt": "2026-05-17T12:00:00"
  },
  "meta": {
    "traceId": "uuid"
  }
}
```

| 필드                 | 타입     | 설명                       |
| -------------------- | -------- | -------------------------- |
| approvalId           | Long     | 카드 승인 ID               |
| cardId               | Long     | 카드 ID                    |
| accountTransactionId | Long     | 생성된 은행 거래 ID        |
| merchantName         | String   | 가맹점명                   |
| merchantCategory     | String   | 가맹점 카테고리 (nullable) |
| approvalAmount       | Decimal  | 결제 금액                  |
| approvalStatus       | String   | APPROVED                   |
| balanceAfter         | Decimal  | 결제 후 계좌 잔액          |
| approvedAt           | DateTime | 결제 시각                  |

### Error Cases

| 상황           | 코드         | 메시지                        |
| -------------- | ------------ | ----------------------------- |
| 카드 없음      | CARD_001     | 카드를 찾을 수 없습니다       |
| 본인 카드 아님 | CARD_002     | 본인 카드가 아닙니다          |
| 잔액 부족      | TRANSFER_002 | 잔액이 부족합니다             |
| 연결 계좌 없음 | ACCOUNT_001  | 해당 계좌를 찾을 수 없습니다  |
| 계좌 이상 상태 | ACCOUNT_003  | 계좌 상태가 유효하지 않습니다 |
