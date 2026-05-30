# mydata-server API 명세

> **Base URL:** `/mydata/v1`
> **Port:** 8084
> **사용 구간:** 외부 서비스 <-> Mydata Server

---

## 공통 헤더

| 헤더             | 설명                  | 필수 |
| ---------------- | --------------------- | ---- |
| X-Firebase-Uid   | Firebase 사용자 식별 ID | O    |
| X-Trace-Id       | 요청 추적 ID           | O    |

> JWT 인증 없음.
> Firebase UID 헤더 기반으로 사용자를 식별합니다.

---

# MYDATA API

---

## 1-1. 마이데이터 연동

**POST** `/connect`

**Request Body**

```json
{
  "provider": "SHINHAN_BANK"
}
```

| 필드     | 타입   | 필수 | 설명           |
| -------- | ------ | ---- | -------------- |
| provider | String | O    | 연동할 기관 코드 |

**Response** `200 OK`

```json
{
  "success": true,
  "data": {
    "connected": true,
    "bankLinked": true,
    "stockLinked": false
  },
  "meta": { "traceId": "uuid" }
}
```

| 필드        | 타입    | 설명           |
| ----------- | ------- | -------------- |
| connected   | Boolean | 연동 성공 여부  |
| bankLinked  | Boolean | 은행 연동 여부  |
| stockLinked | Boolean | 증권 연동 여부  |

| 상황           | 코드      | 메시지                       |
| -------------- | --------- | ---------------------------- |
| 헤더 누락      | VALID_001 | 입력값 오류                  |

---

## 1-2. 연동 목록 조회

**GET** `/connections`

**Request Header:** `X-Firebase-Uid` 필요

**Request Body** 없음

**Response** `200 OK`

```json
{
  "success": true,
  "data": {
    "bankAccounts": [
      {
        "accountId": 1001,
        "accountNumber": "110-123-456789",
        "accountName": "내 급여통장",
        "bankCode": "088",
        "balance": 3500000
      }
    ],
    "stockAccounts": [
      {
        "accountId": 2001,
        "accountNumber": "300-123-456789",
        "accountName": "내 주식 계좌",
        "bankCode": "039"
      }
    ]
  },
  "meta": { "traceId": "uuid" }
}
```

| 필드         | 타입  | 설명             |
| ------------ | ----- | ---------------- |
| bankAccounts | Array | 연동된 은행 계좌 목록 |
| stockAccounts| Array | 연동된 증권 계좌 목록 |

---

## 1-3. 동기화 요청

**POST** `/sync`

**Request Header:** `X-Firebase-Uid` 필요

**Request Body** 없음

**Response** `200 OK`

```json
{
  "success": true,
  "data": {
    "synced": true,
    "syncedAt": "2026-05-26T10:00:00"
  },
  "meta": { "traceId": "uuid" }
}
```

| 필드     | 타입          | 설명         |
| -------- | ------------- | ------------ |
| synced   | Boolean       | 동기화 성공 여부 |
| syncedAt | LocalDateTime | 동기화 시각   |

---

# BANK API

---

## MYDATA-BANK-ACCOUNT-001. 계좌 조회

**GET** `/bank/accounts`

**Request Header:** `X-Firebase-Uid` 필요

### Response `200 OK`

```json
{
  "success": true,
  "data": [
    {
      "accountId": 1001,
      "accountNumber": "110-123-456789",
      "accountName": "내 급여통장",
      "bankCode": "088",
      "balance": 3500000
    }
  ],
  "meta": {
    "traceId": "uuid"
  }
}
```

| 필드          | 타입   | 설명      |
| ------------- | ------ | --------- |
| accountId     | Long   | 계좌 ID   |
| accountNumber | String | 계좌번호  |
| accountName   | String | 계좌명    |
| bankCode      | String | 은행 코드 |
| balance       | Long   | 잔액      |

### Error Codes

| 상황             | 코드     | 메시지                       |
| ---------------- | -------- | ---------------------------- |
| 은행 API 호출 오류 | BANK_500 | 은행 API 호출 중 오류가 발생했습니다 |

---

## MYDATA-BANK-ACCOUNT-002. 계좌 상세 조회

**GET** `/bank/accounts/{accountId}`

### Response `200 OK`

```json
{
  "success": true,
  "data": {
    "accountId": 1001,
    "accountNumber": "110-123-456789",
    "accountName": "내 급여통장",
    "bankCode": "088",
    "accountStatus": "ACTIVE",
    "balance": 3500000
  },
  "meta": {
    "traceId": "uuid"
  }
}
```

| 필드          | 타입   | 설명      |
| ------------- | ------ | --------- |
| accountId     | Long   | 계좌 ID   |
| accountNumber | String | 계좌번호  |
| accountName   | String | 계좌명    |
| bankCode      | String | 은행 코드 |
| accountStatus | String | 계좌 상태 |
| balance       | Long   | 잔액      |

### Error Codes

| 상황      | 코드        | 메시지          |
| --------- | ----------- | --------------- |
| 계좌 없음 | ACCOUNT_001 | 계좌 없음        |

---

## MYDATA-BANK-ACCOUNT-003. 잔액 조회

**GET** `/bank/accounts/{accountId}/balance`

### Response `200 OK`

```json
{
  "success": true,
  "data": {
    "accountId": 1001,
    "balance": 3500000,
    "availableBalance": 3200000
  },
  "meta": {
    "traceId": "uuid"
  }
}
```

| 필드             | 타입 | 설명          |
| ---------------- | ---- | ------------- |
| accountId        | Long | 계좌 ID       |
| balance          | Long | 잔액          |
| availableBalance | Long | 출금 가능 잔액 |

### Error Codes

| 상황      | 코드        | 메시지   |
| --------- | ----------- | -------- |
| 계좌 없음 | ACCOUNT_001 | 계좌 없음 |

---

## MYDATA-BANK-ACCOUNT-004. 거래내역 조회

**GET** `/bank/accounts/{accountId}/transactions`

### Query Parameters

| 이름     | 타입    | 필수 | 설명                     |
| -------- | ------- | ---- | ------------------------ |
| fromDate | String  | X    | 조회 시작일 (YYYY-MM-DD) |
| toDate   | String  | X    | 조회 종료일 (YYYY-MM-DD) |
| page     | Integer | X    | 페이지 번호 (기본값: 0)  |
| size     | Integer | X    | 페이지 크기 (기본값: 20) |

### Response `200 OK`

```json
{
  "success": true,
  "data": [
    {
      "transactionId": 9001,
      "transactionDateTime": "2026-05-01T09:00:00",
      "transactionType": "DEPOSIT",
      "amount": 3000000,
      "balanceAfter": 3500000,
      "description": "급여"
    }
  ],
  "meta": {
    "traceId": "uuid"
  }
}
```

| 필드                | 타입   | 설명        |
| ------------------- | ------ | ----------- |
| transactionId       | Long   | 거래 ID     |
| transactionDateTime | String | 거래 발생일시 |
| transactionType     | String | 거래 유형    |
| amount              | Long   | 거래 금액    |
| balanceAfter        | Long   | 거래 후 잔액 |
| description         | String | 거래 적요    |

### Error Codes

| 상황           | 코드      | 메시지                     |
| -------------- | --------- | -------------------------- |
| 날짜 형식 오류 | VALID_001 | 날짜 형식은 YYYY-MM-DD여야 합니다 |
| 계좌 없음      | ACCOUNT_001 | 계좌 없음                  |

---

## MYDATA-BANK-ACCOUNT-005. 거래 카테고리 조회

**GET** `/bank/accounts/{accountId}/transactions/categories`

### Response `200 OK`

```json
{
  "success": true,
  "data": [
    {
      "category": "급여",
      "amount": 3000000
    },
    {
      "category": "식비",
      "amount": 280000
    }
  ],
  "meta": {
    "traceId": "uuid"
  }
}
```

| 필드     | 타입   | 설명          |
| -------- | ------ | ------------- |
| category | String | 거래 카테고리  |
| amount   | Long   | 카테고리별 금액 |

### Error Codes

| 상황      | 코드        | 메시지    |
| --------- | ----------- | --------- |
| 계좌 없음 | ACCOUNT_001 | 계좌 없음 |

---

# STOCK API

---

## MYDATA-STOCK-ACCOUNT-001. 주문 가능 계좌 조회

**GET** `/stock/accounts`

**Request Header:** `X-Firebase-Uid` 필요

### Response `200 OK`

```json
{
  "success": true,
  "data": [
    {
      "accountId": 2001,
      "accountNumber": "300-123-456789",
      "accountName": "내 주식 계좌",
      "bankCode": "039"
    }
  ],
  "meta": {
    "traceId": "uuid"
  }
}
```

| 필드          | 타입   | 설명      |
| ------------- | ------ | --------- |
| accountId     | Long   | 계좌 ID   |
| accountNumber | String | 계좌번호  |
| accountName   | String | 계좌명    |
| bankCode      | String | 증권사 코드 |

### Error Codes

| 상황           | 코드               | 메시지                    |
| -------------- | ------------------ | ------------------------- |
| 증권 계좌 없음 | STOCK_ACCOUNT_001  | 증권 계좌를 찾을 수 없습니다 |

---

## MYDATA-STOCK-HOLDING-001. 보유 종목 조회

**GET** `/stock/accounts/{accountId}/holdings`

### Response `200 OK`

```json
{
  "success": true,
  "data": [
    {
      "stockCode": "005930",
      "stockName": "삼성전자",
      "quantity": 20,
      "averagePrice": 78000,
      "currentPrice": 82000,
      "evaluationAmount": 1640000,
      "profitRate": 5.12
    }
  ],
  "meta": {
    "traceId": "uuid"
  }
}
```

| 필드             | 타입   | 설명      |
| ---------------- | ------ | --------- |
| stockCode        | String | 종목 코드 |
| stockName        | String | 종목명    |
| quantity         | Long   | 보유 수량 |
| averagePrice     | Long   | 평균 매입가 |
| currentPrice     | Long   | 현재가    |
| evaluationAmount | Long   | 평가 금액 |
| profitRate       | Double | 수익률    |

### Error Codes

| 상황           | 코드               | 메시지            |
| -------------- | ------------------ | ----------------- |
| 보유 종목 없음 | STOCK_HOLDING_001  | 보유 종목이 없습니다 |

---

## MYDATA-STOCK-PORTFOLIO-001. 포트폴리오 조회

**GET** `/stock/accounts/{accountId}/portfolio`

### Response `200 OK`

```json
{
  "success": true,
  "data": {
    "totalEvaluationAmount": 15000000,
    "totalPurchaseAmount": 13200000,
    "totalProfitAmount": 1800000,
    "totalProfitRate": 13.64
  },
  "meta": {
    "traceId": "uuid"
  }
}
```

| 필드                  | 타입   | 설명       |
| --------------------- | ------ | ---------- |
| totalEvaluationAmount | Long   | 총 평가 금액 |
| totalPurchaseAmount   | Long   | 총 매입 금액 |
| totalProfitAmount     | Long   | 총 평가 손익 |
| totalProfitRate       | Double | 총 수익률   |

### Error Codes

| 상황               | 코드                  | 메시지                  |
| ------------------ | --------------------- | ----------------------- |
| 포트폴리오 정보 없음 | STOCK_PORTFOLIO_001   | 포트폴리오 정보가 없습니다 |

---

## MYDATA-STOCK-RETURN-001. 수익률 조회

**GET** `/stock/accounts/{accountId}/returns`

### Response `200 OK`

```json
{
  "success": true,
  "data": {
    "totalPurchaseAmount": 13200000,
    "totalEvaluationAmount": 15000000,
    "totalProfitAmount": 1800000,
    "totalProfitRate": 13.64
  },
  "meta": {
    "traceId": "uuid"
  }
}
```

| 필드                  | 타입   | 설명       |
| --------------------- | ------ | ---------- |
| totalPurchaseAmount   | Long   | 총 매입 금액 |
| totalEvaluationAmount | Long   | 총 평가 금액 |
| totalProfitAmount     | Long   | 총 평가 손익 |
| totalProfitRate       | Double | 총 수익률   |

### Error Codes

| 상황           | 코드               | 메시지             |
| -------------- | ------------------ | ------------------ |
| 수익률 정보 없음 | STOCK_RETURN_001   | 수익률 정보가 없습니다 |

---

## MYDATA-STOCK-ASSET-001. 자산 요약 조회

**GET** `/stock/assets/summary`

**Request Header:** `X-Firebase-Uid` 필요

### Response `200 OK`

```json
{
  "success": true,
  "data": {
    "totalAssetAmount": 18000000,
    "totalPurchaseAmount": 13200000,
    "totalEvaluationAmount": 15000000,
    "totalProfitAmount": 1800000,
    "totalProfitRate": 13.64
  },
  "meta": {
    "traceId": "uuid"
  }
}
```

| 필드                  | 타입   | 설명             |
| --------------------- | ------ | ---------------- |
| totalAssetAmount      | Long   | 총 자산 금액      |
| totalPurchaseAmount   | Long   | 총 매입 금액      |
| totalEvaluationAmount | Long   | 총 평가 금액      |
| totalProfitAmount     | Long   | 총 평가 손익      |
| totalProfitRate       | Double | 총 수익률        |

### Error Codes

| 상황               | 코드              | 메시지                  |
| ------------------ | ----------------- | ----------------------- |
| 자산 요약 정보 없음 | STOCK_ASSET_001   | 자산 요약 정보가 없습니다 |

---

# AGGREGATION API

> **Base Path:** `/mydata/v1/assets`
> 은행/증권 자산을 통합하여 집계한 결과를 제공합니다.

---

## MYDATA-ASSET-001. 통합 자산 요약 조회

**GET** `/assets/summary`

**Request Header:** `X-Firebase-Uid` 필요

### Response `200 OK`

```json
{
  "success": true,
  "data": {
    "totalAssetAmount": 18000000,
    "totalBankAssetAmount": 3000000,
    "totalStockAssetAmount": 15000000,
    "investmentRatio": 83.33
  },
  "meta": {
    "traceId": "uuid"
  }
}
```

| 필드                  | 타입   | 설명                |
| --------------------- | ------ | ------------------- |
| totalAssetAmount      | Long   | 총 자산 합산 금액    |
| totalBankAssetAmount  | Long   | 은행 자산 금액       |
| totalStockAssetAmount | Long   | 증권 자산 금액       |
| investmentRatio       | Double | 투자 비중 (%)        |

### Error Codes

| 상황               | 코드            | 메시지                    |
| ------------------ | --------------- | ------------------------- |
| 마이데이터 연동 실패 | MYDATA_003      | 마이데이터 연동 실패        |
| 자산 집계 오류     | AGGREGATION_001 | 자산 집계 중 오류가 발생했습니다 |

---

## MYDATA-ASSET-002. 자산 분포 조회

**GET** `/assets/distribution`

**Request Header:** `X-Firebase-Uid` 필요

### Response `200 OK`

```json
{
  "success": true,
  "data": {
    "totalAssetAmount": 18000000,
    "totalBankAssetAmount": 3000000,
    "totalStockAssetAmount": 15000000,
    "bankRatio": 16.67,
    "stockRatio": 83.33
  },
  "meta": {
    "traceId": "uuid"
  }
}
```

| 필드                  | 타입   | 설명              |
| --------------------- | ------ | ----------------- |
| totalAssetAmount      | Long   | 총 자산 합산 금액  |
| totalBankAssetAmount  | Long   | 은행 자산 금액     |
| totalStockAssetAmount | Long   | 증권 자산 금액     |
| bankRatio             | Double | 은행 자산 비중 (%) |
| stockRatio            | Double | 증권 자산 비중 (%) |

### Error Codes

| 상황               | 코드            | 메시지                    |
| ------------------ | --------------- | ------------------------- |
| 마이데이터 연동 실패 | MYDATA_003      | 마이데이터 연동 실패        |
| 자산 집계 오류     | AGGREGATION_001 | 자산 집계 중 오류가 발생했습니다 |

---

## MYDATA-ASSET-003. 통합 자산 대시보드 조회

**GET** `/assets/dashboard`

**Request Header:** `X-Firebase-Uid` 필요

### Response `200 OK`

```json
{
  "success": true,
  "data": {
    "totalAssetAmount": 18000000,
    "totalBankAssetAmount": 3000000,
    "totalStockAssetAmount": 15000000,
    "investmentRatio": 83.33,
    "bankAccountCount": 2,
    "holdingCount": 5,
    "totalProfitRate": 13.64
  },
  "meta": {
    "traceId": "uuid"
  }
}
```

| 필드                  | 타입    | 설명                    |
| --------------------- | ------- | ----------------------- |
| totalAssetAmount      | Long    | 총 자산 합산 금액        |
| totalBankAssetAmount  | Long    | 은행 자산 금액           |
| totalStockAssetAmount | Long    | 증권 자산 금액           |
| investmentRatio       | Double  | 투자 비중 (%)            |
| bankAccountCount      | Integer | 연동된 은행 계좌 수      |
| holdingCount          | Integer | 보유 종목 수             |
| totalProfitRate       | Double  | 증권 전체 수익률 (%)     |

### Error Codes

| 상황               | 코드            | 메시지                    |
| ------------------ | --------------- | ------------------------- |
| 마이데이터 연동 실패 | MYDATA_003      | 마이데이터 연동 실패        |
| 자산 집계 오류     | AGGREGATION_001 | 자산 집계 중 오류가 발생했습니다 |
