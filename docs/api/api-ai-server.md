# service-ai-server API 명세

> Base URL: `/api/v1` | Port: `8000`

---

## AI CHAT API

| Method | URL                                    | 설명                | 인증     |
|--------|----------------------------------------|-------------------|--------|
| POST   | /ai/chat/sessions                      | 채팅 세션 생성          | Bearer |
| POST   | /ai/chat/messages                      | 메시지 전송 및 AI 응답 생성 | Bearer |
| DELETE | /ai/chat/sessions/{sessionId}          | 채팅 세션 종료          | Bearer |
| GET    | /ai/chat/sessions                      | 채팅 세션 목록 조회       | Bearer |
| GET    | /ai/chat/sessions/{sessionId}/messages | 채팅 메시지 목록 조회      | Bearer |

---

## AI DISTRIBUTION API

| Method | URL                               | 설명          | 인증     |
|--------|-----------------------------------|-------------|--------|
| POST   | /distributions/settings           | 분배 설정       | Bearer |
| POST   | /distributions/settings/apply     | 분배 설정 적용    | Bearer |
| POST   | /ai/distributions/recommendations | AI 분배 추천 생성 | Bearer |

> 분배 실행은 service-backend `/transfers` 통해 실행

---

## ACTION STATUS API

| Method | URL                            | 설명             | 인증     |
|--------|--------------------------------|----------------|--------|
| GET    | /ai/actions/{actionId}/status  | 금융 실행 상태 조회    | Bearer |
| GET    | /ai/actions/{actionId}/failure | 실패 원인 조회       | Bearer |
| GET    | /ai/actions/history            | 통합 금융 실행 이력 조회 | Bearer |

---

## AI STOCKS API

| Method | URL                     | 설명          | 인증     |
|--------|-------------------------|-------------|--------|
| GET    | /ai/stocks/accounts     | 주문 가능 계좌 조회 | Bearer |
| GET    | /ai/stocks/cash-balance | 예수금 조회      | Bearer |