# transaction-server API 명세

> Base URL: `/api/v1` | Port: `8083`

---

## EVENT PLATFORM API

| Method | URL                                     | 설명            | 인증           |
|--------|-----------------------------------------|---------------|--------------|
| GET    | /admin/events/dlq                       | DLQ 이벤트 조회    | Bearer+ADMIN |
| POST   | /admin/events/dlq/{eventId}/retry       | DLQ 이벤트 재처리   | Bearer+ADMIN |
| GET    | /admin/events/outbox                    | Outbox 이벤트 조회 | Bearer+ADMIN |
| GET    | /admin/events/sagas                     | Saga 목록 조회    | Bearer+ADMIN |
| GET    | /admin/events/sagas/{sagaId}            | Saga 상세 조회    | Bearer+ADMIN |
| POST   | /admin/events/sagas/{sagaId}/compensate | Saga 보상 처리    | Bearer+ADMIN |
| GET    | /admin/events/reconciliation            | 정합성 검증 결과 조회  | Bearer+ADMIN |
| POST   | /admin/events/reconciliation/run        | 정합성 검증 실행     | Bearer+ADMIN |