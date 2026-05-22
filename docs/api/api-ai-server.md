# service-ai-server API 명세

> Base URL: `/api/v1` | Port: `8000`

---

## 에러 코드

| 코드 | 설명 |
| --- | --- |
| AI_001 | AI 응답 생성 실패 |
| AI_002 | LLM 응답 Timeout |
| AI_003 | AI 실행 실패 |
| AI_004 | 이미 종료(CLOSED) 처리된 세션입니다 |

---

## 14-1. 채팅 세션 생성
**POST** `/api/v1/ai/chat/sessions` | Bearer Token 필요

**Request Body**
```json
{
  "title": "자산 상담"
}
```

| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| title | String | X | 세션 제목 |

**Response** `201 Created`
```json
{
  "success": true,
  "data": {
    "sessionId": 1,
    "status": "ACTIVE"
  },
  "meta": { "traceId": "uuid" }
}
```

---

## 14-2. 채팅 세션 목록 조회
**GET** `/api/v1/ai/chat/sessions` | Bearer Token 필요

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
        "sessionId": 1,
        "title": "자산 상담",
        "status": "ACTIVE",
        "createdAt": "2026-05-17T12:00:00"
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

## 14-3. 메시지 전송
**POST** `/api/v1/ai/chat/messages` | Bearer Token 필요

**Request Body**
```json
{
  "sessionId": 1,
  "message": "이번달 소비 분석해줘"
}
```

| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| sessionId | Long | O | 채팅 세션 ID |
| message | String | O | 사용자 메시지 |

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "messageId": 1001,
    "role": "AI",
    "intent": "ASSET",
    "content": "이번달 식비 소비가 증가했습니다.",
    "actionRequired": false
  },
  "meta": { "traceId": "uuid" }
}
```

| 상황 | 코드 | 메시지 |
| --- | --- | --- |
| AI 응답 실패 | AI_001 | AI 응답 생성에 실패했습니다 |

---

## 14-4. 채팅 메시지 목록 조회
**GET** `/api/v1/ai/chat/sessions/messages` | Bearer Token 필요

**Query Parameters**

| 이름 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| sessionId | Long | O | 채팅 세션 ID |
| page | Integer | X | 페이지 (default: 0) |
| size | Integer | X | 사이즈 (default: 20) |

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "content": [
      {
        "messageId": 1001,
        "role": "USER",
        "content": "이번달 소비 분석해줘",
        "createdAt": "2026-05-17T12:00:00"
      },
      {
        "messageId": 1002,
        "role": "AI",
        "intent": "ASSET",
        "content": "이번달 식비 소비가 증가했습니다.",
        "actionRequired": false,
        "createdAt": "2026-05-17T12:00:01"
      }
    ],
    "page": 0,
    "size": 20,
    "totalElements": 2,
    "totalPages": 1
  },
  "meta": { "traceId": "uuid" }
}
```

---

## 14-5. 채팅 세션 종료
**DELETE** `/api/v1/ai/chat/sessions/{sessionId}` | Bearer Token 필요

**Request Body** 없음

**Response** `200 OK`
```json
{
  "success": true,
  "data": {
    "sessionId": 1,
    "status": "CLOSED"
  },
  "meta": { "traceId": "uuid" }
}
```