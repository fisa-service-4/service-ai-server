# api-convention.md

# API convention

## Base URL

```
/api/v1
```

---

## 인증 방식

```
Authorization: Bearer {accessToken}
```

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
    "code": "AUTH_001",
    "message": "에러 메시지"
  },
  "meta": {
    "traceId": "uuid"
  }
}
```

---

## 페이지네이션

### 요청

```
?page=0&size=20
```

### 응답

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

## HTTP 상태 코드

| 상황     | 코드                        |
|--------|---------------------------|
| 조회 성공  | 200 OK                    |
| 생성 성공  | 201 Created               |
| 비동기 요청 | 202 Accepted              |
| 유효성 실패 | 400 Bad Request           |
| 인증 실패  | 401 Unauthorized          |
| 권한 없음  | 403 Forbidden             |
| 리소스 없음 | 404 Not Found             |
| 서버 오류  | 500 Internal Server Error |

---

## URL 네이밍 규칙

```
소문자 + 하이픈 사용
/favorite-stocks      O
/favoriteStocks       X

복수형 사용
/users                O
/user                 X

계층 구조
/accounts/{accountId}/transactions
```

---

## Request/Response 필드 네이밍

```
camelCase 사용
notificationConsentYn   O
notification_consent_yn X
```

---

## 날짜 형식

```
ISO 8601
"2026-05-17T12:00:00"
```

---

## 거래 API 추가 헤더

```
Pin-Token: {pinToken}
Idempotency-Key: {uuid}
```