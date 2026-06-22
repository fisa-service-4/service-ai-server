# db-transaction-spec.md

# Transaction DB 명세서

거래 DB는 분산 트랜잭션 및 이벤트 기반 금융 처리를 위한 데이터를 관리합니다.

Saga Pattern, Transactional Outbox Pattern, Idempotency 처리,
Dead Letter Queue(DLQ), 정합성 검증(Reconciliation) 데이터를 저장합니다.

금융 서비스 특성상 거래 이벤트 추적, 감사(Audit), 장애 복구 및 재처리를 지원합니다.

---

## 테이블 목록

| 테이블명                  | 설명                   |
|-----------------------|----------------------|
| USER_MASTER           | 사용자 식별 정보            |
| USER_ACCOUNT_MAPPING  | 사용자-계좌 매핑            |
| TRANSFER_USER_MAPPING | 이체-사용자 매핑            |
| ORDER_USER_MAPPING    | 주문-사용자 매핑            |
| OUTBOX_EVENT          | Outbox 이벤트 저장        |
| SAGA_TRANSACTION      | Saga 트랜잭션 상태         |
| SAGA_STEP_HISTORY     | Saga 단계별 처리 이력       |
| IDEMPOTENCY_KEY       | 중복 요청 방지 키           |
| DEAD_LETTER_EVENT     | 실패 이벤트 저장            |
| RECONCILIATION_RESULT | 정합성 검증 결과            |
| TRANSACTION_AUDIT_LOG | 금융 거래 감사 로그          |

---

## USER_MASTER

> Transaction Server에서 사용자를 식별하기 위한 최소 정보를 저장합니다.

| 컬럼명          | 데이터 타입       | 설명                    | Null 허용 | PK / FK |
|--------------|--------------|------------------------|---------|---------|
| user_id      | NUMBER(19)   | Transaction Server 내부 PK | NO   | PK      |
| x_user_id    | NUMBER(19)   | 외부 서비스 사용자 ID         | NO      | -       |
| firebase_uid | VARCHAR2(128)| Firebase UID            | YES     | UNIQUE  |
| user_name    | VARCHAR2(100)| 사용자명                   | NO      | -       |
| phone_number | VARCHAR2(20) | 전화번호                   | NO      | -       |
| linked_at    | TIMESTAMP    | 연동 시각                  | YES     | -       |
| created_at   | TIMESTAMP    | 생성 시각 (기본값: SYSTIMESTAMP) | NO  | -       |

---

## USER_ACCOUNT_MAPPING

> 사용자와 계좌 간의 소유 관계를 저장합니다.

| 컬럼명          | 데이터 타입      | 설명                           | Null 허용 | PK / FK |
|-------------|-------------|------------------------------|---------|---------|
| account_id  | NUMBER(19)  | 계좌 ID                        | NO      | PK      |
| account_type| VARCHAR2(10)| 계좌 유형 (BANK / STOCK)         | NO      | PK      |
| user_id     | NUMBER(19)  | Transaction Server 내부 사용자 ID | NO      | -       |
| x_user_id   | NUMBER(19)  | 외부 서비스 사용자 ID               | NO      | -       |
| created_at  | TIMESTAMP   | 생성 시각 (기본값: SYSTIMESTAMP)    | NO      | -       |

> 복합 PK: (account_id, account_type)

---

## TRANSFER_USER_MAPPING

> 이체 건과 요청 사용자 간의 소유 관계를 저장합니다.

| 컬럼명         | 데이터 타입     | 설명                        | Null 허용 | PK / FK |
|-------------|------------|---------------------------|---------|---------|
| transfer_id | NUMBER(19) | 이체 ID                     | NO      | PK      |
| x_user_id   | NUMBER(19) | 외부 서비스 사용자 ID             | NO      | -       |
| created_at  | TIMESTAMP  | 생성 시각 (기본값: SYSTIMESTAMP) | NO      | -       |

---

## ORDER_USER_MAPPING

> 주문 건과 요청 사용자 간의 소유 관계를 저장합니다.

| 컬럼명        | 데이터 타입     | 설명                        | Null 허용 | PK / FK |
|------------|------------|---------------------------|---------|---------|
| order_id   | NUMBER(19) | 주문 ID                     | NO      | PK      |
| x_user_id  | NUMBER(19) | 외부 서비스 사용자 ID             | NO      | -       |
| created_at | TIMESTAMP  | 생성 시각 (기본값: SYSTIMESTAMP) | NO      | -       |

---

## OUTBOX_EVENT

> Transactional Outbox Pattern 기반 이벤트 저장 테이블입니다.

| 컬럼명            | 데이터 타입        | 설명                        | Null 허용 | PK / FK |
|----------------|---------------|---------------------------|---------|---------|
| outbox_id      | NUMBER(19)    | Outbox 이벤트 ID (IDENTITY)  | NO      | PK      |
| aggregate_type | VARCHAR2(50)  | Aggregate 유형              | NO      | -       |
| aggregate_id   | NUMBER(19)    | Aggregate ID              | NO      | -       |
| event_type     | VARCHAR2(100) | 이벤트 유형                   | NO      | -       |
| topic_name     | VARCHAR2(255) | Kafka Topic 이름            | NO      | -       |
| partition_key  | VARCHAR2(255) | Kafka Partition Key       | YES     | -       |
| payload        | CLOB          | 이벤트 Payload              | NO      | -       |
| headers        | CLOB          | 이벤트 Header               | YES     | -       |
| published_yn   | NUMBER(1)     | 발행 여부 (기본값: 0)           | NO      | -       |
| published_at   | TIMESTAMP     | Kafka 발행 시각              | YES     | -       |
| retry_count    | NUMBER(5)     | 재시도 횟수 (기본값: 0)          | NO      | -       |
| created_at     | TIMESTAMP     | 생성 시각 (기본값: SYSTIMESTAMP) | NO      | -       |

### 인덱스

| 이름                             | 컬럼                        | 설명                  |
|--------------------------------|---------------------------|---------------------|
| idx_outbox_event_unpublished   | published_yn, created_at  | 미발행 이벤트 조회          |

---

## SAGA_TRANSACTION

> Saga 트랜잭션 상태 정보를 저장합니다.

| 컬럼명              | 데이터 타입        | 설명                     | Null 허용 | PK / FK |
|------------------|---------------|--------------------------|---------|---------|
| saga_id          | NUMBER(19)    | Saga ID (IDENTITY)       | NO      | PK      |
| transaction_type | VARCHAR2(50)  | 트랜잭션 유형                 | NO      | -       |
| transaction_key  | VARCHAR2(255) | 거래 식별 키                 | NO      | UNIQUE  |
| saga_status      | VARCHAR2(30)  | Saga 상태                 | NO      | -       |
| current_step     | VARCHAR2(100) | 현재 단계                  | YES     | -       |
| total_steps      | NUMBER(5)     | 전체 단계 수                 | YES     | -       |
| failure_reason   | CLOB          | 실패 사유                  | YES     | -       |
| rollback_yn      | NUMBER(1)     | 롤백 여부 (기본값: 0)         | NO      | -       |
| started_at       | TIMESTAMP     | 시작 시각                  | NO      | -       |
| completed_at     | TIMESTAMP     | 완료 시각                  | YES     | -       |

### saga_status 값

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

| 컬럼명              | 데이터 타입        | 설명               | Null 허용 | PK / FK |
|------------------|---------------|------------------|---------|---------|
| step_history_id  | NUMBER(19)    | Saga 단계 이력 ID (IDENTITY) | NO | PK |
| saga_id          | NUMBER(19)    | Saga ID          | NO      | FK      |
| step_name        | VARCHAR2(100) | 단계명              | NO      | -       |
| step_order       | NUMBER(5)     | 단계 순서            | NO      | -       |
| step_status      | VARCHAR2(30)  | 단계 상태            | NO      | -       |
| request_payload  | CLOB          | 요청 데이터           | YES     | -       |
| response_payload | CLOB          | 응답 데이터           | YES     | -       |
| error_message    | CLOB          | 에러 메시지           | YES     | -       |
| processed_at     | TIMESTAMP     | 처리 시각            | NO      | -       |

### step_status 값

| 값           | 설명    |
|-------------|-------|
| SUCCESS     | 성공    |
| FAILED      | 실패    |
| COMPENSATED | 보상 완료 |

### 인덱스

| 이름                               | 컬럼      | 설명            |
|----------------------------------|---------|---------------|
| idx_saga_step_history_saga_id    | saga_id | Saga별 단계 이력 조회 |

---

## IDEMPOTENCY_KEY

> 중복 요청 방지(Idempotency) 처리를 위한 테이블입니다.

| 컬럼명              | 데이터 타입        | 설명                        | Null 허용 | PK / FK |
|------------------|---------------|---------------------------|---------|---------|
| idempotency_key  | VARCHAR2(255) | Idempotency Key           | NO      | PK      |
| request_hash     | VARCHAR2(255) | 요청 해시값                    | NO      | -       |
| request_type     | VARCHAR2(100) | 요청 유형                     | NO      | -       |
| response_payload | CLOB          | 응답 데이터                    | YES     | -       |
| status           | VARCHAR2(30)  | 처리 상태                     | NO      | -       |
| expired_at       | TIMESTAMP     | 만료 시각                     | YES     | -       |
| created_at       | TIMESTAMP     | 생성 시각 (기본값: SYSTIMESTAMP) | NO      | -       |

### status 값

| 값          | 설명   |
|------------|------|
| PROCESSING | 처리 중 |
| SUCCESS    | 성공   |
| FAILED     | 실패   |

---

## DEAD_LETTER_EVENT

> 재처리에 실패한 이벤트를 저장합니다.

| 컬럼명            | 데이터 타입        | 설명                        | Null 허용 | PK / FK |
|----------------|---------------|---------------------------|---------|---------|
| dead_letter_id | NUMBER(19)    | DLQ 이벤트 ID (IDENTITY)    | NO      | PK      |
| original_topic | VARCHAR2(255) | 원본 Kafka Topic            | NO      | -       |
| consumer_group | VARCHAR2(255) | Consumer Group            | YES     | -       |
| payload        | CLOB          | 실패 Payload                | YES     | -       |
| error_message  | CLOB          | 에러 메시지                   | YES     | -       |
| stack_trace    | CLOB          | Stack Trace               | YES     | -       |
| retry_count    | NUMBER(5)     | 재시도 횟수 (기본값: 0)          | NO      | -       |
| resolved_yn    | NUMBER(1)     | 해결 여부 (기본값: 0)           | NO      | -       |
| resolved_at    | TIMESTAMP     | 해결 시각                    | YES     | -       |
| created_at     | TIMESTAMP     | 생성 시각 (기본값: SYSTIMESTAMP) | NO      | -       |

---

## RECONCILIATION_RESULT

> 금융 데이터 정합성 검증 결과를 저장합니다.

| 컬럼명                   | 데이터 타입        | 설명                   | Null 허용 | PK / FK |
|-----------------------|---------------|----------------------|---------|---------|
| reconciliation_id     | NUMBER(19)    | 정합성 검증 ID (IDENTITY) | NO      | PK      |
| reconciliation_type   | VARCHAR2(100) | 정합성 검증 유형            | NO      | -       |
| source_system         | VARCHAR2(100) | 원본 시스템               | NO      | -       |
| target_system         | VARCHAR2(100) | 대상 시스템               | NO      | -       |
| source_count          | NUMBER(19)    | 원본 데이터 수             | YES     | -       |
| target_count          | NUMBER(19)    | 대상 데이터 수             | YES     | -       |
| mismatch_count        | NUMBER(19)    | 불일치 데이터 수            | YES     | -       |
| reconciliation_status | VARCHAR2(30)  | 검증 상태                | NO      | -       |
| checked_at            | TIMESTAMP     | 검증 시각                | NO      | -       |

### reconciliation_status 값

| 값       | 설명 |
|---------|----|
| SUCCESS | 성공 |
| FAILED  | 실패 |

---

## TRANSACTION_AUDIT_LOG

> 금융 거래 감사(Audit) 로그를 저장합니다.

| 컬럼명                      | 데이터 타입        | 설명                    | Null 허용 | PK / FK |
|--------------------------|---------------|----------------------|---------|---------|
| transaction_audit_log_id | NUMBER(19)    | 감사 로그 ID (IDENTITY)   | NO      | PK      |
| transaction_type         | VARCHAR2(100) | 거래 유형                 | NO      | -       |
| transaction_key          | VARCHAR2(255) | 거래 식별 키               | NO      | -       |
| transaction_status       | VARCHAR2(50)  | 거래 상태                 | NO      | -       |
| source_system            | VARCHAR2(100) | 요청 시스템                | NO      | -       |
| target_system            | VARCHAR2(100) | 대상 시스템                | YES     | -       |
| request_payload          | CLOB          | 요청 데이터                | YES     | -       |
| response_payload         | CLOB          | 응답 데이터                | YES     | -       |
| audited_at               | TIMESTAMP     | 감사 시각                 | NO      | -       |

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
- 사용자-계좌/이체/주문 소유권 매핑 관리 (USER_MASTER, *_MAPPING 테이블)
