# service-backend API 명세

> Base URL: `/api/v1` | Port: `8080`
> **사용 구간:** Client ↔ Transaction Server

---

## 공통 헤더

| 헤더 | 설명 | 필수 |
| --- | --- | --- |
| Authorization | Bearer {accessToken} | 인증 필요 API |
| Pin-Token | {pinToken} | 금융 거래 API |
| Idempotency-Key | {uuid} | 이체/주문 API |

## 공통 응답 포맷

**성공**
```json
{
  "success": true,
  "data": {},
  "meta": { "traceId": "uuid" }
}
```

**실패**
```json
{
  "success": false,
  "error": {
    "code": "AUTH_001",
    "message": "에러 메시지"
  },
  "meta": { "traceId": "uuid" }
}
```

**페이지네이션**
```
요청: ?page=0&size=20
```
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
  "meta": { "traceId": "uuid" }
}
```

---

## 에러 코드

| 코드 | 설명 |
| --- | --- |
| AUTH_001 | 이미 가입된 이메일 |
| AUTH_002 | 이미 가입된 전화번호 |
| AUTH_003 | 이메일 또는 비밀번호 불일치 |
| AUTH_004 | 만료된 토큰 |
| AUTH_005 | 유효하지 않은 토큰 |
| AUTH_006 | 휴대폰 인증번호 불일치 |
| AUTH_007 | 만료된 인증번호 |
| AUTH_008 | PIN 불일치 |
| AUTH_009 | PIN 잠금 상태 |
| AUTH_010 | 연속/반복 숫자 PIN 불가 |
| AUTH_011 | 본인 확인 실패 |
| USER_001 | 사용자를 찾을 수 없음 |
| MYDATA_001 | 이미 연동된 기관 |
| MYDATA_002 | 연동 정보를 찾을 수 없음 |
| ADMIN_001 | 관리자 권한 필요 |
| ACCOUNT_001 | 계좌를 찾을 수 없음 |
| ACCOUNT_002 | 본인 계좌가 아닌 경우 접근 불가 |
| ACCOUNT_003 | 계좌 상태가 LOCKED 또는 CLOSED |
| TRANSFER_001 | 이체 건을 찾을 수 없음 |
| TRANSFER_002 | 잔액 부족 |
| TRANSFER_003 | 이미 처리 완료된 이체 |
| TRANSFER_004 | 본인 이체 건이 아닌 경우 접근 불가 |
| MATCHING_001 | 매칭 정보를 찾을 수 없음 |
| MATCHING_002 | 이미 매칭 처리된 건 |
| MATCHING_003 | matched_by가 USER가 아닌 경우 |
| ORDER_001 | 주문 가능 금액 부족 |
| ORDER_002 | 보유 수량 부족 |
| AI_001 | AI 응답 생성 실패 |

---

# AUTH API

---

## 1-1. 회원가입
**POST** `/api/v1/auth/signup` | 인증 불필요

**Request Body**
```json
{
  "email": "user@test.com",
  "password": "Password123!",
  "userName": "홍길동",
  "phoneNumber: "01012345678"
  "jobType": "DEVELOPER",
  "freelancerYn": true,
  "termsConsentYn": true
}
```

| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| email | String | O | 이메일 형식 |
| password | String | O | 영문+숫자+특수문자 8자 이상 |
| name | String | O | 이름 |
| jobType | String | O | 직업 유형 |
| freelancerYn | Boolean | O | 프리랜서 여부 |
| termsConsentYn | Boolean | O | 서비스 이용 동의 (true 필수) |

**Response** `201 Created`
```json
{
  "success": true,
  "data": {
    "userId": 1,
    "email": "user@test.com",
    "name": "홍길동"
  },
  "meta": { "traceId": "uuid" }
}
```

| 상황 | 코드 | 메시지 |
| --- | --- | --- |
| 중복 이메일 | AUTH_001 | 이미 가입된 이메일입니다 |
| 유효성 실패 | VALID_001 | 입력값이 올바르지 않습니다 |

---

## 1-2. 휴대폰 인증 요청
**POST** `/api/v1/auth/phone/send` | 인증 불필요

**Request Body**
```json
{
  "name": "홍길동",
  "residentNumber": "9001011",
  "telecom": "KT",
  "phoneNumber": "01012341234"
}
```

| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| name | String | O | 이름 |
| residentNumber | String | O | 주민번호 앞 7자리 |
| telecom | String | O | SKT / KT / LGU / SKT_MVNO / KT_MVNO / LGU_MVNO |
| phoneNumber | String | O | 휴대폰 번호 (숫자만) |

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "expiredIn": 180
  },
  "meta": { "traceId": "uuid" }
}
```

| 상황 | 코드 | 메시지 |
| --- | --- | --- |
| 중복 전화번호 | AUTH_002 | 이미 가입된 전화번호입니다 |
| 본인 확인 실패 | AUTH_011 | 본인 확인에 실패했습니다 |

---

## 1-3. 휴대폰 인증 검증
**POST** `/api/v1/auth/phone/verify` | 인증 불필요

**Request Body**
```json
{
  "phoneNumber": "01012341234",
  "verificationCode": "123456"
}
```

| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| phoneNumber | String | O | 휴대폰 번호 |
| verificationCode | String | O | 인증번호 6자리 |

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "verified": true
  },
  "meta": { "traceId": "uuid" }
}
```

| 상황 | 코드 | 메시지 |
| --- | --- | --- |
| 인증번호 불일치 | AUTH_006 | 인증번호가 올바르지 않습니다 |
| 인증번호 만료 | AUTH_007 | 인증번호가 만료되었습니다 |

---

## 1-4. PIN 등록
**POST** `/api/v1/auth/pin` | Bearer Token 필요

**Request Body**
```json
{
  "pin": "123456",
  "pinConfirm": "123456"
}
```

| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| pin | String | O | 6자리 숫자 PIN |
| pinConfirm | String | O | PIN 확인 |

**Response** `201 Created`
```json
{
  "success": true,
  "data": {
    "registered": true
  },
  "meta": { "traceId": "uuid" }
}
```

| 상황 | 코드 | 메시지 |
| --- | --- | --- |
| PIN 불일치 | AUTH_008 | PIN이 일치하지 않습니다 |
| 연속/반복 숫자 | AUTH_010 | 연속 또는 반복 숫자는 사용할 수 없습니다 |

---

## 1-5. PIN 검증
**POST** `/api/v1/auth/pin/verify` | Bearer Token 필요

**Request Body**
```json
{
  "pin": "123456"
}
```

| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| pin | String | O | 6자리 PIN |

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "matched": true,
    "pinToken": "TEMP_PIN_TOKEN",
    "failCount": 0,
    "lockedYn": false
  },
  "meta": { "traceId": "uuid" }
}
```

| 상황 | 코드 | 메시지 |
| --- | --- | --- |
| PIN 불일치 | AUTH_008 | PIN이 올바르지 않습니다. 잔여 N회 |
| PIN 잠금 | AUTH_009 | PIN이 잠겼습니다. 고객센터에 문의해주세요 |

---

## 1-6. PIN 변경
**PATCH** `/api/v1/auth/pin` | Bearer Token 필요

**Request Body**
```json
{
  "oldPin": "123456",
  "newPin": "654321"
}
```

| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| oldPin | String | O | 기존 PIN |
| newPin | String | O | 새 PIN |

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "changed": true
  },
  "meta": { "traceId": "uuid" }
}
```

| 상황 | 코드 | 메시지 |
| --- | --- | --- |
| 기존 PIN 불일치 | AUTH_008 | 기존 PIN이 올바르지 않습니다 |
| 연속/반복 숫자 | AUTH_010 | 연속 또는 반복 숫자는 사용할 수 없습니다 |

---

## 1-7. 로그인
**POST** `/api/v1/auth/login` | 인증 불필요

**Request Body**
```json
{
  "email": "user@test.com",
  "password": "Password123!"
}
```

| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| email | String | O | 이메일 |
| password | String | O | 비밀번호 |

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "accessToken": "jwt-access-token",
    "refreshToken": "jwt-refresh-token",
    "user": {
      "userId": 1,
      "name": "홍길동",
      "email": "user@test.com"
    }
  },
  "meta": { "traceId": "uuid" }
}
```

| 상황 | 코드 | 메시지 |
| --- | --- | --- |
| 인증 실패 | AUTH_003 | 이메일 또는 비밀번호가 올바르지 않습니다 |

---

## 1-8. 로그아웃
**POST** `/api/v1/auth/logout` | Bearer Token 필요

**Request Body** 없음

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "message": "로그아웃 완료"
  },
  "meta": { "traceId": "uuid" }
}
```

---

## 1-10. 회원가입 완료
**POST** `/api/v1/auth/signup/complete` | Bearer Token 필요

**Request Body** 없음

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "accessToken": "jwt-access-token",
    "refreshToken": "jwt-refresh-token",
    "userId": 1,
    "name": "홍길동"
  },
  "meta": { "traceId": "uuid" }
}
```

---

## 1-12. 토큰 재발급
**POST** `POST /api/v1/auth/reissue` | 인증 불필요

**Request Body**
```json
{
  "refreshToken": "jwt-refresh-token"
}
```

| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| refreshToken | String | O | 리프레시 토큰 |

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "accessToken": "new-access-token"
  },
  "meta": { "traceId": "uuid" }
}
```

| 상황 | 코드 | 메시지 |
| --- | --- | --- |
| 토큰 만료 | AUTH_004 | 만료된 토큰입니다 |
| 유효하지 않은 토큰 | AUTH_005 | 유효하지 않은 토큰입니다 |

---

# USERS API

---

## 2-1. 내 정보 조회
**GET** `/api/v1/users/me` | Bearer Token 필요

**Request Body** 없음

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "userId": 1,
    "name": "홍길동",
    "email": "user@test.com",
    "phoneNumber": "010****1234",
    "jobType": "DEVELOPER",
    "notificationConsentYn": true,
    "createdAt": "2026-05-01T10:00:00"
  },
  "meta": { "traceId": "uuid" }
}
```

---

## 2-3. 알람 on/off
**PATCH** `/api/v1/users/me/alarm` | Bearer Token 필요

**Request Body**
```json
{
  "notificationConsentYn": false
}
```

| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| notificationConsentYn | Boolean | O | 알림 동의 여부 |

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "notificationConsentYn": false
  },
  "meta": { "traceId": "uuid" }
}
```

---

# MYDATA API

---

## 3-2. 마이데이터 연동
**POST** `/api/v1/mydata/connect` | Bearer Token 필요

**Request Body**
```json
{
  "institutionCode": "004",
  "consentYn": true
}
```

| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| institutionCode | String | O | 연동할 기관 코드 |
| consentYn | Boolean | O | 마이데이터 동의 여부 (true 필수) |

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "linkedAccountId": 1,
    "institutionCode": "004",
    "institutionName": "국민은행",
    "syncedAt": "2026-05-17T12:00:00"
  },
  "meta": { "traceId": "uuid" }
}
```

| 상황 | 코드 | 메시지 |
| --- | --- | --- |
| 이미 연동된 기관 | MYDATA_001 | 이미 연동된 기관입니다 |

---

## 3-4. 연동 목록 조회
**GET** `/api/v1/mydata/connections` | Bearer Token 필요

**Request Body** 없음

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "connections": [
      {
        "linkedAccountId": 1,
        "institutionCode": "004",
        "institutionName": "국민은행",
        "institutionType": "BANK",
        "accountMasking": "****-****-1234",
        "syncedAt": "2026-05-17T12:00:00"
      }
    ]
  },
  "meta": { "traceId": "uuid" }
}
```

---

## 3-6. 동기화 요청
**POST** `/api/v1/mydata/sync` | Bearer Token 필요

**Request Body** 없음

**Response** `202 Accepted`
```json
{
  "success": true,
  "data": {
    "syncRequested": true
  },
  "meta": { "traceId": "uuid" }
}
```

---

# NOTIFICATIONS API

---

## 4-1. 알림 목록 조회
**GET** `/api/v1/notifications` | Bearer Token 필요

**Query Parameters**

| 이름 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| page | Integer | X | 페이지 (default: 0) |
| size | Integer | X | 사이즈 (default: 20) |
| type | String | X | 알림 타입 필터 |

**알림 type**

| 값 | 설명 |
| --- | --- |
| DEPOSIT | 입금 완료 |
| UNMATCHED | 미매칭 입금 |
| DELAYED | 미입금 지연 |
| SALARY | 가상 월급 이체 |
| BALANCE_WARNING | 잔액 부족 경고 |
| AI_BRIEFING | AI 브리핑 |
| SYSTEM | 시스템 알림 |

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "content": [
      {
        "notificationId": 1,
        "type": "AI-BRIEFING",
        "title": "이번달 지출이 너무 많아요",
        "message": "생활비 비율을 줄이고 비상금·투자 비율 조정을 추천해요.",
        "isRead": false,
        "actionType": "ADJUST",
        "actionButtons": [
          { "label": "조정하기", "action": "ADJUST" },
          { "label": "나중에", "action": "LATER" }
        ],
        "createdAt": "2026-05-17T12:00:00"
      }
    ],
    "page": 0,
    "size": 20,
    "totalElements": 5,
    "totalPages": 1,
    "unreadCount": 2
  },
  "meta": { "traceId": "uuid" }
}
```

---

## 4-2. 알림 읽음 처리
**PATCH** `/api/v1/notifications/{id}/read` | Bearer Token 필요

**Request Body** 없음

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "read": true
  },
  "meta": { "traceId": "uuid" }
}
```

---

# 매칭 API

---

## 매칭 목록 조회
**GET** `/api/v1/payment-matchings` | Bearer Token 필요

**Query Parameters**

| 이름 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| contractId | Long | X | 계약 ID 필터 |
| matchingStatus | String | X | MATCHED / FAILED / TBC / MANUAL_MATCHED |
| from | Date | X | 시작일 (YYYY-MM-DD) |
| to | Date | X | 종료일 (YYYY-MM-DD) |

**Response** `200 OK`
```json
{
  "success": true,
  "data": [
    {
      "matchingId": 301,
      "contractId": 101,
      "bankTransactionId": 9001,
      "matchingStatus": "MATCHED",
      "matchedBy": "SYSTEM",
      "matchedAt": "2026-05-01T09:05:00"
    },
    {
      "matchingId": 302,
      "contractId": 102,
      "bankTransactionId": null,
      "matchingStatus": "TBC",
      "matchedBy": "SYSTEM",
      "matchedAtv": null
    }
  ],
  "meta": { "traceId": "uuid" }
}
```

---

## 수동 매칭 처리
**PATCH** `/api/v1/payment-matchings/{matchingId}/manual` | Bearer Token 필요  
**추가 헤더:** `Idempotency-Key: {uuid}`

**Request Body**
```json
{
  "bankTransactionId": 9001,
  "matchedBy": "USER"
}
```

| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| bankTransactionId | Long | O | 매칭할 입금 거래 ID |
| matchedBy | String | O | USER 고정 |

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "matchingId": 302,
    "matchingStatus": "MANUAL_MATCHED",
    "matchedBy": "USER",
    "matchedAt": "2026-05-18T11:00:00"
  },
  "meta": { "traceId": "uuid" }
}
```

| 상황 | 코드 | 메시지 |
| --- | --- | --- |
| 매칭 정보 없음 | MATCHING_001 | 매칭 정보를 찾을 수 없습니다 |
| 이미 처리된 건 | MATCHING_002 | 이미 매칭 처리된 건입니다 |
| matchedBy 오류 | MATCHING_003 | matchedBy는 USER만 허용됩니다 |

---

# 계좌 관리 API

---

## 계좌 역할 설정
**PATCH** `/api/v1/accounts/{accountId}/role` | Bearer Token 필요

> 입금 통장 / 월급 통장 / 비상금 통장 / 주식 계좌 역할 설정

**Request Body**
```json
{
  "accountRole": "SALARY"
}
```

| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| accountRole | String | O | DEPOSIT / SALARY / EMERGENCY / STOCK |

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "accountId": 1001,
    "accountRole": "SALARY",
    "updatedAt": "2026-05-17T12:00:00"
  },
  "meta": { "traceId": "uuid" }
}
```

---

# ACCOUNTS API

---

## 5-1. 내 계좌 조회
**GET** `/api/v1/accounts` | Bearer Token 필요

**Query Parameters**

| 이름 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| status | String | X | ACTIVE / DORMANT / LOCKED / CLOSED |

**Response** `200 OK`
```json
{
  "success": true,
  "data": [
    {
      "accountId": 1001,
      "bankCode": "088",
      "accountNumber": "110-123-456789",
      "accountName": "내 급여통장",
      "balance": 3500000,
      "accountStatus": "ACTIVE",
      "accountRole": "SALARY"
    }
  ],
  "meta": { "traceId": "uuid" }
}
```

---

## 5-2. 계좌 상세 조회
**GET** `/api/v1/accounts/{accountId}` | Bearer Token 필요

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "accountId": 1001,
    "userId": 501,
    "bankCode": "088",
    "accountNumber": "110-123-456789",
    "accountName": "내 급여통장",
    "balance": 3500000,
    "availableBalance": 3200000,
    "accountStatus": "ACTIVE",
    "accountRole": "SALARY",
    "openedAt": "2024-01-15T09:00:00",
    "closedAt": null,
    "updatedAt": "2026-05-17T14:22:00"
  },
  "meta": { "traceId": "uuid" }
}
```

| 상황 | 코드 | 메시지 |
| --- | --- | --- |
| 계좌 없음 | ACCOUNT_001 | 해당 계좌를 찾을 수 없습니다 |
| 접근 불가 | ACCOUNT_002 | 본인 계좌가 아닙니다 |

---

## 5-3. 잔액 조회
**GET** `/api/v1/accounts/{accountId}/balance` | Bearer Token 필요

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "accountId": 1001,
    "balance": 3500000,
    "availableBalance": 3200000,
    "updatedAt": "2026-05-18T10:15:00"
  },
  "meta": { "traceId": "uuid" }
}
```

| 상황 | 코드 | 메시지 |
| --- | --- | --- |
| 계좌 없음 | ACCOUNT_001 | 해당 계좌를 찾을 수 없습니다 |
| 접근 불가 | ACCOUNT_002 | 본인 계좌가 아닙니다 |

---

## 5-4. 거래내역 조회
**GET** `/api/v1/accounts/{accountId}/transactions` | Bearer Token 필요

**Query Parameters**

| 이름 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| from | Date | X | 조회 시작일 (YYYY-MM-DD) |
| to | Date | X | 조회 종료일 (YYYY-MM-DD) |
| page | Integer | X | 페이지 번호 (default: 0) |
| size | Integer | X | 페이지 크기 (default: 20) |

**Response** `200 OK`
```json
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
        "transactionStatus": "SUCCESS",
        "transactionAt": "2026-05-01T09:00:00"
      }
    ],
    "page": 0,
    "size": 20,
    "totalElements": 42,
    "totalPages": 3
  },
  "meta": { "traceId": "uuid" }
}
```

| 상황 | 코드 | 메시지 |
| --- | --- | --- |
| 날짜 형식 오류 | VALID_001 | 입력값이 올바르지 않습니다 |
| 계좌 없음 | ACCOUNT_001 | 해당 계좌를 찾을 수 없습니다 |
| 접근 불가 | ACCOUNT_002 | 본인 계좌가 아닙니다 |

---

## 5-5. 거래내역 필터 조회
**GET** `/api/v1/accounts/{accountId}/transactions/filter` | Bearer Token 필요

**Query Parameters**

| 이름 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| type | String | X | DEPOSIT / WITHDRAW / TRANSFER_IN / TRANSFER_OUT / AUTO_TRANSFER |
| channel | String | X | APP / AI_AGENT |
| status | String | X | SUCCESS / FAILED / CANCELLED |
| from | Date | X | 조회 시작일 (YYYY-MM-DD) |
| to | Date | X | 조회 종료일 (YYYY-MM-DD) |
| minAmount | Decimal | X | 최소 거래 금액 |
| maxAmount | Decimal | X | 최대 거래 금액 |
| page | Integer | X | 페이지 번호 (default: 0) |
| size | Integer | X | 페이지 크기 (default: 20) |

**Response** `200 OK`
```json
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
  "meta": { "traceId": "uuid" }
}
```

---

# TRANSFERS API

---

## 6-1. 이체 요청
**POST** `/api/v1/transfers` | Bearer Token 필요  
**추가 헤더:** `Idempotency-Key: {uuid}`

**Request Body**
```json
{
  "fromAccountId": 1001,
  "toBankCode": "020",
  "toAccountNumber": "301-0987-1234",
  "transferAmount": 500000,
  "requestedBy": "USER"
}
```

| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| fromAccountId | Long | O | 출금 계좌 ID |
| toBankCode | String | O | 입금 은행 코드 |
| toAccountNumber | String | O | 입금 계좌번호 |
| transferAmount | Decimal | O | 이체 금액 (0 초과) |
| requestedBy | String | O | USER / AI |

**Response** `201 Created`
```json
{
  "success": true,
  "data": {
    "transferId": 5001,
    "transferStatus": "REQUESTED",
    "requestedAt": "2026-05-18T10:30:00"
  },
  "meta": { "traceId": "uuid" }
}
```

| 상황 | 코드 | 메시지 |
| --- | --- | --- |
| 잔액 부족 | TRANSFER_002 | 잔액이 부족합니다 |
| 계좌 이상 상태 | ACCOUNT_003 | 계좌 상태가 유효하지 않습니다 |
| 접근 불가 | ACCOUNT_002 | 본인 계좌가 아닙니다 |

---

## 6-2. 이체 승인
**POST** `/api/v1/transfers/{transferId}/approve` | Bearer Token 필요

**Request Body** 없음

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "transferId": 5001,
    "transferStatus": "SUCCESS",
    "completedAt": "2026-05-18T10:30:05"
  },
  "meta": { "traceId": "uuid" }
}
```

| 상황 | 코드 | 메시지 |
| --- | --- | --- |
| 이체 건 없음 | TRANSFER_001 | 해당 이체 건을 찾을 수 없습니다 |
| 중복 승인 | TRANSFER_003 | 이미 처리 완료된 이체입니다 |

---

## 6-3. 이체 결과 조회
**GET** `/api/v1/transfers/{transferId}` | Bearer Token 필요

**Response** `200 OK`
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
  "meta": { "traceId": "uuid" }
}
```

| 상황 | 코드 | 메시지 |
| --- | --- | --- |
| 이체 건 없음 | TRANSFER_001 | 해당 이체 건을 찾을 수 없습니다 |
| 접근 불가 | TRANSFER_004 | 본인 이체 건이 아닙니다 |

---

# STOCKS API

---

## 7-1. 종목 검색
**GET** `/api/v1/stocks/search` | Bearer Token 필요

**Query Parameters**

| 이름 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| keyword | String | O | 종목명 또는 종목코드 |

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "stocks": [
      {
        "stockCode": "005930",
        "stockName": "삼성전자",
        "market": "KOSPI",
        "currentPrice": 82000,
        "changeRate": -1.2
      }
    ]
  },
  "meta": { "traceId": "uuid" }
}
```

---

## 7-2. 현재가 조회
**GET** `/api/v1/stocks/{stockCode}/price` | Bearer Token 필요

**Response** `200 OK`
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
  "meta": { "traceId": "uuid" }
}
```

---

## 7-3. 차트 조회
**GET** `/api/v1/stocks/{stockCode}/chart` | Bearer Token 필요

**Query Parameters**

| 이름 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| interval | String | O | DAILY / WEEKLY / MONTHLY |
| from | Date | X | 시작일 (YYYY-MM-DD) |
| to | Date | X | 종료일 (YYYY-MM-DD) |

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "stockCode": "005930",
    "candles": [
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
  "meta": { "traceId": "uuid" }
}
```

---

## 7-4. 주문 가능 계좌 조회
**GET** `/api/v1/stocks/accounts` | Bearer Token 필요

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "accounts": [
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

---

## 7-5. 예수금 조회
**GET** `/api/v1/stocks/cash-balance` | Bearer Token 필요

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "cashBalance": 3000000,
    "availableBalance": 2800000
  },
  "meta": { "traceId": "uuid" }
}
```

---

# ORDERS API

---

## 8-1. 주식 주문 생성
**POST** `/api/v1/orders` | Bearer Token 필요  
**추가 헤더:** `Pin-Token: {pinToken}`, `Idempotency-Key: {uuid}`

**Request Body**
```json
{
  "stockCode": "005930",
  "orderType": "BUY",
  "orderMethod": "LIMIT",
  "quantity": 10,
  "price": 82000
}
```

| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| stockCode | String | O | 종목 코드 |
| orderType | String | O | BUY / SELL |
| orderMethod | String | O | MARKET / LIMIT |
| quantity | Integer | O | 주문 수량 |
| price | Integer | X | 주문 가격 (LIMIT 시 필수, MARKET 시 null) |

**Response** `201 Created`
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
  "meta": { "traceId": "uuid" }
}
```

| 상황 | 코드 | 메시지 |
| --- | --- | --- |
| 주문 가능 금액 부족 | ORDER_001 | 주문 가능 금액이 부족합니다 |
| 보유 수량 부족 | ORDER_002 | 보유 수량이 부족합니다 |

---

## 8-2. 주문 취소
**POST** `/api/v1/orders/{orderId}/cancel` | Bearer Token 필요  
**추가 헤더:** `Pin-Token: {pinToken}`, `Idempotency-Key: {uuid}`

**Request Body** 없음

**Response** `200 OK`
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
  "meta": { "traceId": "uuid" }
}
```

---

## 8-3. 주문 내역 조회
**GET** `/api/v1/orders` | Bearer Token 필요

**Query Parameters**

| 이름 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| status | String | X | REQUESTED / PARTIAL_FILLED / FILLED / CANCELLED / FAILED |
| orderType | String | X | BUY / SELL |
| page | Integer | X | 페이지 (default: 0) |
| size | Integer | X | 페이지 크기 (default: 20) |

**Response** `200 OK`
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
  "meta": { "traceId": "uuid" }
}
```

---

## 8-4. 주문 상세 조회
**GET** `/api/v1/orders/{orderId}` | Bearer Token 필요

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "orderId": 1001,
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
  "meta": { "traceId": "uuid" }
}
```

---

# EXECUTIONS API

---

## 9-1. 체결 내역 조회
**GET** `/api/v1/executions` | Bearer Token 필요

**Query Parameters**

| 이름 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| stockCode | String | X | 종목 코드 |
| from | Date | X | 시작일 (YYYY-MM-DD) |
| to | Date | X | 종료일 (YYYY-MM-DD) |
| page | Integer | X | 페이지 (default: 0) |
| size | Integer | X | 페이지 크기 (default: 20) |

**Response** `200 OK`
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
  "meta": { "traceId": "uuid" }
}
```

---

# HOLDINGS API

---

## 10-1. 보유 종목 조회
**GET** `/api/v1/holdings` | Bearer Token 필요

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "holdings": [
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
  "meta": { "traceId": "uuid" }
}
```

---

## 10-2. 수익률 조회
**GET** `/api/v1/holdings/returns` | Bearer Token 필요

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "dailyReturnRate": 1.5,
    "monthlyReturnRate": 7.3,
    "yearlyReturnRate": 18.1
  },
  "meta": { "traceId": "uuid" }
}
```

---

# PORTFOLIO API

---

## 11-1. 포트폴리오 조회
**GET** `/api/v1/portfolio` | Bearer Token 필요

**Response** `200 OK`
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
  "meta": { "traceId": "uuid" }
}
```

---

# FAVORITE STOCKS API

---

## 12-1. 관심종목 등록
**POST** `/api/v1/favorite-stocks` | Bearer Token 필요

**Request Body**
```json
{
  "stockCode": "005930"
}
```

| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| stockCode | String | O | 종목 코드 |

**Response** `201 Created`
```json
{
  "success": true,
  "data": {
    "favoriteId": 1,
    "stockCode": "005930"
  },
  "meta": { "traceId": "uuid" }
}
```

---

## 12-2. 관심종목 삭제
**DELETE** `/api/v1/favorite-stocks/{favoriteId}` | Bearer Token 필요

**Request Body** 없음

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "deleted": true
  },
  "meta": { "traceId": "uuid" }
}
```

---

## 12-3. 관심종목 목록 조회
**GET** `/api/v1/favorite-stocks` | Bearer Token 필요

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "favorites": [
      {
        "favoriteId": 1,
        "stockCode": "005930",
        "stockName": "삼성전자",
        "currentPrice": 82000,
        "changeRate": -1.2
      }
    ]
  },
  "meta": { "traceId": "uuid" }
}
```

---

# VIRTUAL SALARY API

---

## 13-1. 가상월급 조회
**GET** `/api/v1/virtual-salary` | Bearer Token 필요

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "monthlySalary": 3000000,
    "savingRatio": 40,
    "investmentRatio": 30
  },
  "meta": { "traceId": "uuid" }
}
```

---

## 13-2. 가상월급 설정 저장
**POST** `/api/v1/virtual-salary` | Bearer Token 필요

**Request Body**
```json
{
  "monthlySalary": 3000000,
  "savingRatio": 40,
  "investmentRatio": 30
}
```

| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| monthlySalary | Integer | O | 월급 금액 |
| savingRatio | Integer | O | 저축 비율 |
| investmentRatio | Integer | O | 투자 비율 |

> **정책:** savingRatio + investmentRatio <= 100

**Response** `201 Created`
```json
{
  "success": true,
  "data": {
    "saved": true
  },
  "meta": { "traceId": "uuid" }
}
```

---

## 13-3. AI 추천 비율 조회
**GET** `/api/v1/virtual-salary/recommendation` | Bearer Token 필요

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "recommendedMonthlySalary": 2500000,
    "recommendedSavingRatio": 50,
    "recommendedInvestmentRatio": 30,
    "reason": "최근 수입 안정성이 높아 투자 비중 확대를 추천합니다."
  },
  "meta": { "traceId": "uuid" }
}
```


---

# DISTRIBUTIONS API

---

## 15-1. 분배 설정
**POST** `/api/v1/distributions/settings` | Bearer Token 필요  
**추가 헤더:** `Pin-Token: {pinToken}`, `Idempotency-Key: {uuid}`

**Request Body**
```json
{
  "incomeAmount": 5000000,
  "confirmed": true
}
```

| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| incomeAmount | Long | O | 분배 대상 수입 금액 |
| confirmed | Boolean | O | 실행 확인 여부 (true 필수) |

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "distributionId": 8001,
    "status": "COMPLETED"
  },
  "meta": { "traceId": "uuid" }
}
```

---

# ACTIONS API

---

## 16-1. 실행 상태 조회
**GET** `/api/v1/actions/{actionId}/status` | Bearer Token 필요

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "actionId": 1001,
    "actionType": "TRANSFER",
    "status": "COMPLETED",
    "updatedAt": "2026-05-17T12:05:00"
  },
  "meta": { "traceId": "uuid" }
}
```

---

## 16-2. Saga 상태 조회
**GET** `/api/v1/actions/{actionId}/saga` | Bearer Token 필요

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "sagaId": 3001,
    "actionId": 1001,
    "status": "SUCCESS",
    "steps": [
      {
        "stepName": "TRANSFER_REQUEST",
        "stepStatus": "SUCCESS",
        "executedAt": "2026-05-17T12:00:00"
      },
      {
        "stepName": "TRANSFER_APPROVE",
        "stepStatus": "SUCCESS",
        "executedAt": "2026-05-17T12:00:05"
      }
    ]
  },
  "meta": { "traceId": "uuid" }
}
```

---

## 16-3. 실패 원인 조회
**GET** `/api/v1/actions/{actionId}/failure` | Bearer Token 필요

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "actionId": 1001,
    "failedStep": "TRANSFER_APPROVE",
    "errorCode": "TRANSFER_002",
    "errorMessage": "잔액이 부족합니다.",
    "failedAt": "2026-05-17T12:01:00"
  },
  "meta": { "traceId": "uuid" }
}
```

---

## 16-4. 실행 이력 조회
**GET** `/api/v1/actions/history` | Bearer Token 필요

**Query Parameters**

| 이름 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| page | Integer | X | 페이지 (default: 0) |
| size | Integer | X | 사이즈 (default: 20) |

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "content": [
      {
        "actionId": 1001,
        "actionType": "TRANSFER",
        "status": "COMPLETED",
        "createdAt": "2026-05-17T12:00:00"
      }
    ],
    "page": 0,
    "size": 20,
    "totalElements": 10,
    "totalPages": 1
  },
  "meta": { "traceId": "uuid" }
}
```

---

# ADMIN API

---

## 17-1. 사용자 목록 조회
**GET** `/api/v1/admin/users` | Bearer Token 필요 (ADMIN 권한)

**Query Parameters**

| 이름 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| page | Integer | X | 페이지 (default: 0) |
| size | Integer | X | 사이즈 (default: 20) |
| keyword | String | X | 이름/이메일 검색 |
| status | String | X | ACTIVE / INACTIVE / SUSPENDED / WITHDRAW |
| jobType | String | X | 직업 유형 필터 |

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "content": [
      {
        "userId": 1,
        "name": "홍길동",
        "email": "user@test.com",
        "jobType": "DEVELOPER",
        "freelancerYn": true,
        "status": "ACTIVE",
        "createdAt": "2026-05-01T10:00:00",
        "lastLoginAt": "2026-05-17T10:00:00"
      }
    ],
    "page": 0,
    "size": 20,
    "totalElements": 100,
    "totalPages": 5
  },
  "meta": { "traceId": "uuid" }
}
```

---

## 17-2. 사용자 상세 조회
**GET** `/api/v1/admin/users/{id}` | Bearer Token 필요 (ADMIN 권한)

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "userId": 1,
    "name": "홍길동",
    "email": "user@test.com",
    "phoneNumber": "010****1234",
    "jobType": "DEVELOPER",
    "freelancerYn": true,
    "status": "ACTIVE",
    "termsConsentYn": true,
    "mydataConsentYn": true,
    "notificationConsentYn": true,
    "createdAt": "2026-05-01T10:00:00",
    "lastLoginAt": "2026-05-17T10:00:00"
  },
  "meta": { "traceId": "uuid" }
}
```

---

## 17-3. 사용자 상태 변경
**PATCH** `/api/v1/admin/users/{id}/status` | Bearer Token 필요 (ADMIN 권한)

**Request Body**
```json
{
  "status": "SUSPENDED"
}
```

| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| status | String | O | ACTIVE / INACTIVE / SUSPENDED / WITHDRAW |

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "userId": 1,
    "status": "SUSPENDED"
  },
  "meta": { "traceId": "uuid" }
}
```

---

## 17-4. 로그인 로그 조회
**GET** `/api/v1/admin/logs/login` | Bearer Token 필요 (ADMIN 권한)

**Query Parameters**

| 이름 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| page | Integer | X | 페이지 (default: 0) |
| size | Integer | X | 사이즈 (default: 20) |
| userId | Long | X | 사용자 ID 필터 |
| loginType | String | X | LOGIN / LOGOUT / FAIL |
| startDate | String | X | 시작 날짜 (yyyy-MM-dd) |
| endDate | String | X | 종료 날짜 (yyyy-MM-dd) |

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "content": [
      {
        "loginHistoryId": 1,
        "userId": 1,
        "userName": "홍길동",
        "loginType": "LOGIN",
        "ipAddress": "127.0.0.1",
        "device": "iPhone / iOS 17",
        "failReason": null,
        "loggedAt": "2026-05-17T10:00:00"
      }
    ],
    "page": 0,
    "size": 20,
    "totalElements": 500,
    "totalPages": 25
  },
  "meta": { "traceId": "uuid" }
}
```

---

## 17-5. AI 로그 조회
**GET** `/api/v1/admin/logs/ai` | Bearer Token 필요 (ADMIN 권한)

**Query Parameters**

| 이름 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| page | Integer | X | 페이지 (default: 0) |
| size | Integer | X | 사이즈 (default: 20) |
| userId | Long | X | 사용자 ID 필터 |
| startDate | String | X | 시작 날짜 (yyyy-MM-dd) |
| endDate | String | X | 종료 날짜 (yyyy-MM-dd) |

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "content": [
      {
        "aiUsageLogId": 1,
        "userId": 1,
        "userName": "홍길동",
        "sessionId": 10,
        "modelName": "qwen3-32b",
        "requestType": "CHAT",
        "responseTimeMs": 1230,
        "successYn": true,
        "createdAt": "2026-05-17T10:00:00"
      }
    ],
    "page": 0,
    "size": 20,
    "totalElements": 300,
    "totalPages": 15
  },
  "meta": { "traceId": "uuid" }
}
```

---

## 17-6. 오류 로그 조회
**GET** `/api/v1/admin/logs/error` | Bearer Token 필요 (ADMIN 권한)

**Query Parameters**

| 이름 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| page | Integer | X | 페이지 (default: 0) |
| size | Integer | X | 사이즈 (default: 20) |
| errorLevel | String | X | INFO / WARN / ERROR / CRITICAL |
| resolvedYn | Boolean | X | 해결 여부 |
| startDate | String | X | 시작 날짜 (yyyy-MM-dd) |
| endDate | String | X | 종료 날짜 (yyyy-MM-dd) |

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "content": [
      {
        "errorLogId": 1,
        "serviceName": "service-backend",
        "errorLevel": "ERROR",
        "errorCode": "DB_001",
        "errorMessage": "Connection timeout",
        "requestUri": "/api/v1/users/me",
        "resolvedYn": false,
        "createdAt": "2026-05-17T10:00:00"
      }
    ],
    "page": 0,
    "size": 20,
    "totalElements": 50,
    "totalPages": 3
  },
  "meta": { "traceId": "uuid" }
}
```

---

## 17-7. 오류 해결 처리
**PATCH** `/api/v1/admin/logs/error/{id}` | Bearer Token 필요 (ADMIN 권한)

**Request Body**
```json
{
  "resolvedYn": true,
  "resolvedMemo": "DB 연결 설정 수정으로 해결"
}
```

| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| resolvedYn | Boolean | O | 해결 여부 |
| resolvedMemo | String | X | 해결 메모 |

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "errorLogId": 1,
    "resolvedYn": true,
    "resolvedAt": "2026-05-17T12:00:00"
  },
  "meta": { "traceId": "uuid" }
}
```

---

## 17-8. API 로그 조회
**GET** `/api/v1/admin/logs/api` | Bearer Token 필요 (ADMIN 권한)

**Query Parameters**

| 이름 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| page | Integer | X | 페이지 (default: 0) |
| size | Integer | X | 사이즈 (default: 20) |
| serviceName | String | X | 서비스명 필터 |
| startDate | String | X | 시작 날짜 (yyyy-MM-dd) |
| endDate | String | X | 종료 날짜 (yyyy-MM-dd) |

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "content": [
      {
        "apiLogId": 1,
        "traceId": "trace-abc-123",
        "serviceName": "service-backend",
        "apiName": "/api/v1/users/me",
        "httpMethod": "GET",
        "responseCode": "200",
        "durationMs": 120,
        "requestedAt": "2026-05-17T10:00:00"
      }
    ],
    "page": 0,
    "size": 20,
    "totalElements": 1000,
    "totalPages": 50
  },
  "meta": { "traceId": "uuid" }
}
```

---

## 17-9. 관리자 대시보드 조회
**GET** `/api/v1/admin/monitoring/dashboard` | Bearer Token 필요 (ADMIN 권한)

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "todayAiRequests": 1245,
    "todayApiCalls": 8541,
    "todayErrors": 23
  },
  "meta": { "traceId": "uuid" }
}
```

---

# EVENT PLATFORM API (보류)

---

## 18-1. DLQ 이벤트 조회
**GET** `/api/v1/admin/events/dlq` | Bearer Token 필요 (ADMIN 권한)

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "events": [
      {
        "eventId": 5001,
        "topic": "ai.transfer.completed",
        "status": "FAILED",
        "failedAt": "2026-05-17T12:00:00"
      }
    ]
  },
  "meta": { "traceId": "uuid" }
}
```

---

## 18-2. DLQ 재처리
**POST** `/api/v1/admin/events/dlq/{eventId}/retry` | Bearer Token 필요 (ADMIN 권한)

**Request Body** 없음

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "eventId": 5001,
    "retryStatus": "SUCCESS"
  },
  "meta": { "traceId": "uuid" }
}
```

---

## 18-3. Outbox 조회
**GET** `/api/v1/admin/events/outbox` | Bearer Token 필요 (ADMIN 권한)

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "events": [
      {
        "outboxId": 1001,
        "topic": "transfer.requested",
        "status": "PENDING",
        "createdAt": "2026-05-17T12:00:00"
      }
    ]
  },
  "meta": { "traceId": "uuid" }
}
```

---

## 18-4. Saga 목록 조회
**GET** `/api/v1/admin/events/sagas` | Bearer Token 필요 (ADMIN 권한)

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "sagas": [
      {
        "sagaId": 3001,
        "actionType": "TRANSFER",
        "status": "FAILED",
        "createdAt": "2026-05-17T12:00:00"
      }
    ]
  },
  "meta": { "traceId": "uuid" }
}
```

---

## 18-5. Saga 상세 조회
**GET** `/api/v1/admin/events/sagas/{sagaId}` | Bearer Token 필요 (ADMIN 권한)

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "sagaId": 3001,
    "actionType": "TRANSFER",
    "status": "FAILED",
    "steps": [
      {
        "stepName": "TRANSFER_REQUEST",
        "stepStatus": "SUCCESS",
        "executedAt": "2026-05-17T12:00:00"
      },
      {
        "stepName": "TRANSFER_APPROVE",
        "stepStatus": "FAILED",
        "errorCode": "TRANSFER_002",
        "executedAt": "2026-05-17T12:00:01"
      }
    ]
  },
  "meta": { "traceId": "uuid" }
}
```

---

## 18-6. Saga 보상 처리
**POST** `/api/v1/admin/events/sagas/{sagaId}/compensate` | Bearer Token 필요 (ADMIN 권한)

**Request Body** 없음

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "sagaId": 3001,
    "status": "COMPENSATED"
  },
  "meta": { "traceId": "uuid" }
}
```

---

## 18-7. 정합성 검증 조회
**GET** `/api/v1/admin/events/reconciliation` | Bearer Token 필요 (ADMIN 권한)

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "reconciliationId": 101,
    "status": "SUCCESS",
    "totalChecked": 1500,
    "mismatchCount": 2,
    "executedAt": "2026-05-17T03:00:00"
  },
  "meta": { "traceId": "uuid" }
}
```

---

## 18-8. 정합성 검증 실행
**POST** `/api/v1/admin/events/reconciliation/run` | Bearer Token 필요 (ADMIN 권한)

**Request Body** 없음

**Response** `202 Accepted`
```json
{
  "success": true,
  "data": {
    "reconciliationId": 102,
    "status": "STARTED"
  },
  "meta": { "traceId": "uuid" }
}
```