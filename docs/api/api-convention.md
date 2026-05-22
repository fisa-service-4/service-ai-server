# api-convention.md

# API Convention

> 전체 서비스 공통 API 규약 정의
>
> 개별 API 스펙은 각 서버 문서에서 관리하고,
> 본 문서는 **공통 규칙 / 네이밍 / 인증 / 응답 형식 / 내부 통신 규약**만 정의한다.

---

# 1. API Domain

| 구분           | Base URL       | 설명                                   |
| ------------ | -------------- | ------------------------------------ |
| External API | `/api/v1`      | Client ↔ Service Backend             |
| BaaS API     | `/baas/v1`     | Transaction Server ↔ Bank/Stock Core |
| Internal API | `/internal/v1` | 내부 서버 간 통신                           |
| MyData API   | `/mydata/v1`   | MyData 서비스 API                       |

---

# 2. 서버 역할 정의

| 서버                 | 역할              |
| ------------------ | --------------- |
| service-backend    | 사용자 API Gateway |
| transaction-server | 금융 트랜잭션 오케스트레이션 |
| bank-server        | 은행 코어           |
| stock-server       | 증권 코어           |
| mydata-server      | 마이데이터 통합        |
| ai-server          | AI 분석 및 추천      |

---

# 3. API Prefix 규칙

## 3-1. External API

```text
/api/v1
```

* 사용자 인증 필요
* Client 전용 API
* JWT 기반 인증 사용

---

## 3-2. BaaS API

```text
/baas/v1/{domain}
```

* Transaction Server → Core Server 호출
* 금융 처리 전용 API
* Saga 기반 분산 처리 대상

---

## 3-3. Internal API

```text
/internal/v1/{domain}
```

* 내부 서버 간 통신 전용
* 외부 공개 금지
* Internal Network 전용

---

## 3-4. MyData API

```text
/mydata/v1
```


* MyData 서버 연동 API
* 통합 자산 조회 전용

---

# 4. 인증 규칙

# 4-1. External API

```http
Authorization: Bearer {accessToken}
```

| Header        | 설명         |
| ------------- | ---------- |
| Authorization | 사용자 인증 JWT |

---

# 4-2. 금융 Write API 추가 Header

```http
Pin-Token: {pinToken}
Idempotency-Key: {uuid}
```

| Header          | 설명           |
| --------------- | ------------ |
| Pin-Token       | PIN 인증 완료 토큰 |
| Idempotency-Key | 중복 요청 방지     |

적용 대상:

* 이체
* 주문
* 자동분배 실행
* 수동 매칭
* 금융 거래 실행 API

---

# 4-3. Internal API

```http
X-User-Id: {userId}
X-Trace-Id: {uuid}
```

| Header     | 설명        |
| ---------- | --------- |
| X-User-Id  | 사용자 식별 ID |
| X-Trace-Id | 요청 추적 ID  |

* 내부 인증 완료 요청만 허용
* JWT 인증 미사용

---

# 5. URL 네이밍 규칙

## 기본 규칙

```text
소문자 + kebab-case 사용
```

예시:

```text
/favorite-stocks
/stock-orders
```

---

## Resource는 복수형 사용

```text
/accounts
/transfers
/orders
```

---

## 계층 구조 사용

```text
/accounts/{accountId}/transactions
/orders/{orderId}/cancel
```

---

# 6. Request / Response 규칙

## JSON Field Naming

```text
camelCase 사용
```

예시:

```json
{
  "accountNumber": "1234567890",
  "transferAmount": 10000
}
```

---

## Boolean Naming

```text
xxxYn 사용
```

예시:

```text
consentYn
lockedYn
deletedYn
```

---

## DateTime Naming

```text
createdAt
updatedAt
requestedAt
completedAt
```

---

# 7. 공통 Response Format

## Success

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

## Error

```json
{
  "success": false,
  "error": {
    "code": "ACCOUNT_001",
    "message": "계좌를 찾을 수 없습니다."
  },
  "meta": {
    "traceId": "uuid"
  }
}
```

---

# 8. Trace ID 규칙

## Header

```http
X-Trace-Id: {uuid}
```

* Request / Response 동일 값 사용
* Saga 추적 및 로그 연계 목적
* 전체 금융 흐름 추적 가능해야 함

---

# 9. Pagination 규칙

## Request

```text
?page=0&size=20
```

---

## Response

```json
{
  "success": true,
  "data": {
    "content": [],
    "page": 0,
    "size": 20,
    "totalElements": 100,
    "totalPages": 5
  }
}
```

---

# 10. 날짜 형식 규칙

## DateTime

```text
ISO-8601
```

## Date

```text
YYYY-MM-DD
```

---

# 11. HTTP Status 규칙

| 상황     | Status                    |
| ------ | ------------------------- |
| 조회 성공  | 200 OK                    |
| 생성 성공  | 201 Created               |
| 비동기 요청 | 202 Accepted              |
| 잘못된 요청 | 400 Bad Request           |
| 인증 실패  | 401 Unauthorized          |
| 권한 없음  | 403 Forbidden             |
| 리소스 없음 | 404 Not Found             |
| 서버 오류  | 500 Internal Server Error |

---

# 12. 금융 Write API 규칙

금융성 API는 반드시 아래 규칙을 따른다.

## 필수 조건

```http
Idempotency-Key: {uuid}
```

---

## 목적

* 중복 실행 방지
* 네트워크 재시도 안정성 확보
* Exactly Once 처리 보조

---

## 적용 대상

* 이체
* 주문 생성
* 주문 취소
* 자동분배 실행
* Saga 실행 API

---

# 13. Saga / 비동기 처리 규칙

## 비동기 처리 응답

```http
202 Accepted
```

```json
{
  "success": true,
  "data": {
    "status": "PROCESSING"
  }
}
```

---

## 상태 조회 API 제공 권장

예시:

```text
/transfers/{transferId}/status
/orders/{orderId}/status
```

---

# 14. Enum 규칙

## Enum Naming

```text
UPPER_SNAKE_CASE
```

예시:

```text
ACTIVE
LOCKED
SUCCESS
FAILED
CANCELLED
```

---

# 15. 보안 규칙

## 민감 정보 마스킹

예시:

```text
010****1234
1234-****-****-5678
```

---

## 저장 금지 정보

다음 정보는 로그 저장 금지:

* PIN 원문
* 비밀번호
* 주민번호
* Access Token
* Refresh Token

---

## PIN 저장 규칙

* PIN 원문 저장 금지
* Hash 저장 필수

---

# 16. API 문서 작성 규칙

각 API 문서는 아래 순서를 따른다.

```md
## API 이름

**METHOD** `/path`

### Description

### Request Header

### Query Parameters

### Path Variables

### Request Body

### Response

### Error Cases
```

---

# 17. Error Code 규칙

```text
{DOMAIN}_{NUMBER}
```

예시:

```text
AUTH_001
ACCOUNT_001
TRANSFER_002
ORDER_001
MYDATA_001
```

---

# 18. 권장 서비스 흐름

```text
Client
  ↓
Service Backend
  ↓
Transaction Server
  ↓
BaaS API
  ↓
Bank / Stock Core
```
