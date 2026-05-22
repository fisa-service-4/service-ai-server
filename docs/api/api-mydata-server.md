# mydata-server API 명세

> Port: `8084`

```

# BANK API

---

## MYDATA-BANK-ACCOUNT-001. 계좌 조회

**GET** `/mydata/v1/accounts`

### Query Parameters

| 이름     | 타입     | 필수 | 설명                                 |
| ------ | ------ | -- | ---------------------------------- |
| status | String | X  | ACTIVE / DORMANT / LOCKED / CLOSED |

### Response `200 OK`

```json id="rqsl7j"
{
  "success": true,
  "data": {
    "content": [
      {
        "accountId": 1001,
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

## MYDATA-BANK-ACCOUNT-002. 계좌 상세 조회

**GET** `/mydata/v1/accounts/{accountId}`

### Response `200 OK`

```json id="u5k5m1"
{
  "success": true,
  "data": {
    "accountId": 1001,
    "bankCode": "088",
    "accountNumber": "110-123-456789",
    "accountName": "내 급여통장",
    "balance": 3500000,
    "availableBalance": 3200000,
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

### Error Codes

| 상황    | 코드          | 메시지              |
| ----- | ----------- | ---------------- |
| 계좌 없음 | ACCOUNT_001 | 해당 계좌를 찾을 수 없습니다 |
| 접근 불가 | ACCOUNT_002 | 본인 계좌가 아닙니다      |

---

## MYDATA-BANK-ACCOUNT-003. 잔액 조회

**GET** `/mydata/v1/accounts/{accountId}/balance`

### Response `200 OK`

```json id="vr3zgd"
{
  "success": true,
  "data": {
    "accountId": 1001,
    "balance": 3500000,
    "availableBalance": 3200000,
    "updatedAt": "2026-05-18T10:15:00"
  },
  "meta": {
    "traceId": "uuid"
  }
}
```

### Error Codes

| 상황    | 코드          | 메시지              |
| ----- | ----------- | ---------------- |
| 계좌 없음 | ACCOUNT_001 | 해당 계좌를 찾을 수 없습니다 |
| 접근 불가 | ACCOUNT_002 | 본인 계좌가 아닙니다      |

---

## MYDATA-BANK-ACCOUNT-004. 거래내역 조회

**GET** `/mydata/v1/accounts/{accountId}/transactions`

### Query Parameters

| 이름        | 타입      | 필수 | 설명                                                              |
| --------- | ------- | -- | --------------------------------------------------------------- |
| type      | String  | X  | DEPOSIT / WITHDRAW / TRANSFER_IN / TRANSFER_OUT / AUTO_TRANSFER |
| channel   | String  | X  | APP / AI_AGENT                                                  |
| status    | String  | X  | SUCCESS / FAILED / CANCELLED                                    |
| fromDate  | Date    | X  | 조회 시작일 (YYYY-MM-DD)                                             |
| toDate    | Date    | X  | 조회 종료일 (YYYY-MM-DD)                                             |
| minAmount | Decimal | X  | 최소 거래 금액                                                        |
| maxAmount | Decimal | X  | 최대 거래 금액                                                        |
| page      | Integer | X  | 페이지 번호 (기본값: 0)                                                 |
| size      | Integer | X  | 페이지 크기 (기본값: 20)                                                |

### Response `200 OK`

```json id="2bh7ph"
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

### Error Codes

| 상황     | 코드          | 메시지              |
| ------ | ----------- | ---------------- |
| 입력값 오류 | VALID_001   | 입력값이 올바르지 않습니다   |
| 계좌 없음  | ACCOUNT_001 | 해당 계좌를 찾을 수 없습니다 |
| 접근 불가  | ACCOUNT_002 | 본인 계좌가 아닙니다      |

---

## MYDATA-BANK-ACCOUNT-005. 거래 카테고리 조회

**GET** `/mydata/v1/accounts/{accountId}/transactions/categories`

### Query Parameters

| 이름       | 타입   | 필수 | 설명                  |
| -------- | ---- | -- | ------------------- |
| fromDate | Date | O  | 집계 시작일 (YYYY-MM-DD) |
| toDate   | Date | O  | 집계 종료일 (YYYY-MM-DD) |

### Response `200 OK`

```json id="0i55gr"
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

### Error Codes

| 상황     | 코드          | 메시지              |
| ------ | ----------- | ---------------- |
| 입력값 오류 | VALID_001   | 입력값이 올바르지 않습니다   |
| 계좌 없음  | ACCOUNT_001 | 해당 계좌를 찾을 수 없습니다 |
| 접근 불가  | ACCOUNT_002 | 본인 계좌가 아닙니다      |


---

# STOCK API

---

## MYDATA-STOCK-ACCOUNT-001. 주문 가능 계좌 조회

**GET** `/mydata/v1/stock/accounts`

### Response `200 OK`

```json id="3z6gpk"
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

## MYDATA-STOCK-HOLDING-001. 보유 종목 조회

**GET** `/mydata/v1/stock/accounts/{accountId}/holdings`

### Query Parameters

| 이름   | 타입      | 필수 | 설명               |
| ---- | ------- | -- | ---------------- |
| page | Integer | X  | 페이지 번호 (기본값: 0)  |
| size | Integer | X  | 페이지 크기 (기본값: 20) |

### Response `200 OK`

```json id="n3a7v0"
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

## MYDATA-STOCK-PORTFOLIO-001. 포트폴리오 조회

**GET** `/mydata/v1/stock/accounts/{accountId}/portfolio`

### Response `200 OK`

```json id="y9b4s1"
{
  "success": true,
  "data": {
    "portfolio": {
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
    }
  },
  "meta": {
    "traceId": "uuid"
  }
}
```

### Portfolio Field 설명

| 필드            | 설명        |
| ------------- | --------- |
| totalAsset    | 총 자산      |
| cashAsset     | 현금성 자산    |
| stockAsset    | 주식 자산     |
| savingAsset   | 예적금 자산    |
| availableCash | 주문 가능 현금  |
| assetRatio    | 자산 비율 (%) |

---

## MYDATA-STOCK-RETURN-001. 수익률 조회

**GET** `/mydata/v1/stock/accounts/{accountId}/returns`

### Response `200 OK`

```json id="fjk8r2"
{
  "success": true,
  "data": {
    "dailyReturnRate": 1.5,
    "monthlyReturnRate": 7.3,
    "yearlyReturnRate": 18.1,
    "updatedAt": "2026-05-18T10:15:00"
  },
  "meta": {
    "traceId": "uuid"
  }
}
```

---

## MYDATA-STOCK-ASSET-001. 자산 요약 조회

**GET** `/mydata/v1/stock/assets/summary`

### Response `200 OK`

```json id="v0y1pu"
{
  "success": true,
  "data": {
    "summary": {
      "totalEvaluationAmount": 15000000,
      "totalPurchaseAmount": 13200000,
      "totalProfit": 1800000,
      "totalProfitRate": 13.64,
      "holdingCount": 8
    }
  },
  "meta": {
    "traceId": "uuid"
  }
}
```

### Summary Field 설명

| 필드                    | 설명      |
| --------------------- | ------- |
| totalEvaluationAmount | 총 평가 금액 |
| totalPurchaseAmount   | 총 매수 금액 |
| totalProfit           | 총 평가 손익 |
| totalProfitRate       | 총 수익률   |
| holdingCount          | 보유 종목 수 |
