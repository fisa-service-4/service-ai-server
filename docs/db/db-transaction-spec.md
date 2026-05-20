# db-transaction-spec.md

# Transaction DB 명세서

거래 DB는 분산 트랜잭션 및 이벤트 기반 금융 처리를 위한 데이터를 관리합니다.

Saga Pattern, Transactional Outbox Pattern, Idempotency 처리,
Dead Letter Queue(DLQ), 정합성 검증(Reconciliation) 데이터를 저장합니다.

금융 서비스 특성상 거래 이벤트 추적, 감사(Audit), 장애 복구 및 재처리를 지원합니다.

---

## 테이블 목록

| 테이블명                  | 설명             |
|-----------------------|----------------|
| OUTBOX_EVENT          | Outbox 이벤트 저장  |
| SAGA_TRANSACTION      | Saga 트랜잭션 상태   |
| SAGA_STEP_HISTORY     | Saga 단계별 처리 이력 |
| IDEMPOTENCY_KEY       | 중복 요청 방지 키     |
| DEAD_LETTER_EVENT     | 실패 이벤트 저장      |
| RECONCILIATION_RESULT | 정합성 검증 결과      |
| TRANSACTION_AUDIT_LOG | 금융 거래 감사 로그    |

---

## OUTBOX_EVENT

> Transactional Outbox Pattern 기반 이벤트 저장 테이블입니다.

| 컬럼명            | 데이터 타입       | 설명                  | Null 허용 | PK / FK |
|----------------|--------------|---------------------|---------|---------|
| outbox_id      | BIGINT       | Outbox 이벤트 ID       | NO      | PK      |
| aggregate_type | VARCHAR(50)  | Aggregate 유형        | NO      | -       |
| aggregate_id   | BIGINT       | Aggregate ID        | NO      | -       |
| event_type     | VARCHAR(100) | 이벤트 유형              | NO      | -       |
| topic_name     | VARCHAR(255) | Kafka Topic 이름      | NO      | -       |
| partition_key  | VARCHAR(255) | Kafka Partition Key | YES     | -       |
| payload        | JSON         | 이벤트 Payload         | NO      | -       |
| headers        | JSON         | 이벤트 Header          | YES     | -       |
| published_yn   | BOOLEAN      | 발행 여부               | NO      | -       |
| published_at   | TIMESTAMP    | Kafka 발행 시각         | YES     | -       |
| retry_count    | INT          | 재시도 횟수              | NO      | -       |
| created_at     | TIMESTAMP    | 생성 시각               | NO      | -       |

---

## SAGA_TRANSACTION

> Saga 트랜잭션 상태 정보를 저장합니다.

| 컬럼명              | 데이터 타입       | 설명      | Null 허용 | PK / FK |
|------------------|--------------|---------|---------|---------|
| saga_id          | BIGINT       | Saga ID | NO      | PK      |
| transaction_type | VARCHAR(50)  | 트랜잭션 유형 | NO      | -       |
| transaction_key  | VARCHAR(255) | 거래 식별 키 | NO      | UNIQUE  |
| saga_status      | ENUM         | Saga 상태 | NO      | -       |
| current_step     | VARCHAR(100) | 현재 단계   | YES     | -       |
| total_steps      | INT          | 전체 단계 수 | YES     | -       |
| failure_reason   | TEXT         | 실패 사유   | YES     | -       |
| rollback_yn      | BOOLEAN      | 롤백 여부   | NO      | -       |
| started_at       | TIMESTAMP    | 시작 시각   | NO      | -       |
| completed_at     | TIMESTAMP    | 완료 시각   | YES     | -       |

### saga_status (ENUM)

| 값            | 설명      |
|--------------|---------|
| STARTED      | 시작      |
| PROCESSING   | 처리 중    |
| SUCCESS      | 성공      |
| FAILED       | 실패      |
| COMPENSATING | 보상 처리 중 |
| COMPENSATED  | 보상 완료   |

---

## SAGA_STEP_HISTORY

> Saga 단계별 처리 이력을 저장합니다.

| 컬럼명              | 데이터 타입       | 설명            | Null 허용 | PK / FK |
|------------------|--------------|---------------|---------|---------|
| step_history_id  | BIGINT       | Saga 단계 이력 ID | NO      | PK      |
| saga_id          | BIGINT       | Saga ID       | NO      | FK      |
| step_name        | VARCHAR(100) | 단계명           | NO      | -       |
| step_order       | INT          | 단계 순서         | NO      | -       |
| step_status      | ENUM         | 단계 상태         | NO      | -       |
| request_payload  | JSON         | 요청 데이터        | YES     | -       |
| response_payload | JSON         | 응답 데이터        | YES     | -       |
| error_message    | TEXT         | 에러 메시지        | YES     | -       |
| processed_at     | TIMESTAMP    | 처리 시각         | NO      | -       |

### step_status (ENUM)

| 값           | 설명    |
|-------------|-------|
| SUCCESS     | 성공    |
| FAILED      | 실패    |
| COMPENSATED | 보상 완료 |

---

## IDEMPOTENCY_KEY

> 중복 요청 방지(Idempotency) 처리를 위한 테이블입니다.

| 컬럼명              | 데이터 타입       | 설명              | Null 허용 | PK / FK |
|------------------|--------------|-----------------|---------|---------|
| idempotency_key  | VARCHAR(255) | Idempotency Key | NO      | PK      |
| request_hash     | VARCHAR(255) | 요청 해시값          | NO      | -       |
| request_type     | VARCHAR(100) | 요청 유형           | NO      | -       |
| response_payload | JSON         | 응답 데이터          | YES     | -       |
| status           | ENUM         | 처리 상태           | NO      | -       |
| expired_at       | TIMESTAMP    | 만료 시각           | YES     | -       |
| created_at       | TIMESTAMP    | 생성 시각           | NO      | -       |

### status (ENUM)

| 값          | 설명   |
|------------|------|
| PROCESSING | 처리 중 |
| SUCCESS    | 성공   |
| FAILED     | 실패   |

---

## DEAD_LETTER_EVENT

> 재처리에 실패한 이벤트를 저장합니다.

| 컬럼명            | 데이터 타입       | 설명             | Null 허용 | PK / FK |
|----------------|--------------|----------------|---------|---------|
| dead_letter_id | BIGINT       | DLQ 이벤트 ID     | NO      | PK      |
| original_topic | VARCHAR(255) | 원본 Kafka Topic | NO      | -       |
| consumer_group | VARCHAR(255) | Consumer Group | YES     | -       |
| payload        | JSON         | 실패 Payload     | YES     | -       |
| error_message  | TEXT         | 에러 메시지         | YES     | -       |
| stack_trace    | LONGTEXT     | Stack Trace    | YES     | -       |
| retry_count    | INT          | 재시도 횟수         | NO      | -       |
| resolved_yn    | BOOLEAN      | 해결 여부          | NO      | -       |
| resolved_at    | TIMESTAMP    | 해결 시각          | YES     | -       |
| created_at     | TIMESTAMP    | 생성 시각          | NO      | -       |

---

## RECONCILIATION_RESULT

> 금융 데이터 정합성 검증 결과를 저장합니다.

| 컬럼명                   | 데이터 타입       | 설명        | Null 허용 | PK / FK |
|-----------------------|--------------|-----------|---------|---------|
| reconciliation_id     | BIGINT       | 정합성 검증 ID | NO      | PK      |
| reconciliation_type   | VARCHAR(100) | 정합성 검증 유형 | NO      | -       |
| source_system         | VARCHAR(100) | 원본 시스템    | NO      | -       |
| target_system         | VARCHAR(100) | 대상 시스템    | NO      | -       |
| source_count          | BIGINT       | 원본 데이터 수  | YES     | -       |
| target_count          | BIGINT       | 대상 데이터 수  | YES     | -       |
| mismatch_count        | BIGINT       | 불일치 데이터 수 | YES     | -       |
| reconciliation_status | ENUM         | 검증 상태     | NO      | -       |
| checked_at            | TIMESTAMP    | 검증 시각     | NO      | -       |

### reconciliation_status (ENUM)

| 값       | 설명 |
|---------|----|
| SUCCESS | 성공 |
| FAILED  | 실패 |

---

## TRANSACTION_AUDIT_LOG

> 금융 거래 감사(Audit) 로그를 저장합니다.

| 컬럼명                      | 데이터 타입       | 설명       | Null 허용 | PK / FK |
|--------------------------|--------------|----------|---------|---------|
| transaction_audit_log_id | BIGINT       | 감사 로그 ID | NO      | PK      |
| transaction_type         | VARCHAR(100) | 거래 유형    | NO      | -       |
| transaction_key          | VARCHAR(255) | 거래 식별 키  | NO      | -       |
| transaction_status       | VARCHAR(50)  | 거래 상태    | NO      | -       |
| source_system            | VARCHAR(100) | 요청 시스템   | NO      | -       |
| target_system            | VARCHAR(100) | 대상 시스템   | YES     | -       |
| request_payload          | JSON         | 요청 데이터   | YES     | -       |
| response_payload         | JSON         | 응답 데이터   | YES     | -       |
| audited_at               | TIMESTAMP    | 감사 시각    | NO      | -       |

---

# 주요 관계

| 부모 테이블           | 자식 테이블            | 설명          |
|------------------|-------------------|-------------|
| SAGA_TRANSACTION | SAGA_STEP_HISTORY | Saga 단계별 이력 |

---

# 설계 특징

- Transactional Outbox Pattern 기반 이벤트 저장
- Saga Pattern 기반 분산 트랜잭션 관리
- Idempotency 기반 중복 요청 방지
- Dead Letter Queue 기반 장애 이벤트 관리
- 금융 감사(Audit) 및 이벤트 추적 지원
- 정합성 검증(Reconciliation) 지원
- Kafka 기반 이벤트 재처리 지원