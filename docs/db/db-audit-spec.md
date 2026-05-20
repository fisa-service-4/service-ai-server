# db-audit-spec.md

# Audit (Log) DB 명세서

로그 DB는 감사(Audit) 및 운영 로그 데이터를 저장합니다.
금융 서비스 특성상 모든 접근 및 행동 이력을 추적하기 위해 운영 DB와 분리하여 관리합니다.

---

## 테이블 목록

| 테이블명                    | 설명                       |
|-------------------------|--------------------------|
| LOGIN_HISTORY           | 로그인/로그아웃 감사 로그           |
| USER_ACTIVITY_LOG       | 사용자 행동 분석 로그             |
| API_CALL_LOG            | MSA/API Gateway Trace 추적 |
| AI_USAGE_LOG            | LLM 호출 및 사용량 추적          |
| AI_PROMPT_LOG           | AI 프롬프트 추적               |
| AI_ACTION_LOG           | AI 금융 액션 감사 로그           |
| SYSTEM_ERROR_LOG        | 시스템 장애 추적                |
| SECURITY_AUDIT_LOG      | 금융 보안 감사 로그              |
| BATCH_EXECUTION_LOG     | 배치 실행 로그                 |
| LANGGRAPH_EXECUTION_LOG | LangGraph Agent 실행 추적    |

---

## LOGIN_HISTORY

> 사용자 로그인/로그아웃 감사 로그

| 컬럼명              | 데이터 타입                        | 설명        | Null 허용 | PK / FK |
|------------------|-------------------------------|-----------|---------|---------|
| login_history_id | BIGINT                        | 로그인 이력 ID | NO      | PK      |
| user_id          | BIGINT                        | 사용자 ID    | NO      | FK      |
| login_type       | ENUM('LOGIN','LOGOUT','FAIL') | 로그인 유형    | NO      | -       |
| ip_address       | VARCHAR(50)                   | IP 주소     | NO      | -       |
| device_info      | VARCHAR(255)                  | 디바이스 정보   | YES     | -       |
| fail_reason      | VARCHAR(255)                  | 실패 사유     | YES     | -       |
| logged_at        | TIMESTAMP                     | 로그인 시각    | NO      | -       |

---

## USER_ACTIVITY_LOG

> 사용자 행동 분석용 로그

| 컬럼명             | 데이터 타입       | 설명          | Null 허용 | PK / FK |
|-----------------|--------------|-------------|---------|---------|
| activity_log_id | BIGINT       | 활동 로그 ID    | NO      | PK      |
| user_id         | BIGINT       | 사용자 ID      | NO      | FK      |
| activity_type   | VARCHAR(100) | 활동 유형       | NO      | -       |
| activity_target | VARCHAR(255) | 대상 리소스      | YES     | -       |
| request_uri     | VARCHAR(500) | 요청 URI      | YES     | -       |
| http_method     | VARCHAR(20)  | HTTP Method | YES     | -       |
| ip_address      | VARCHAR(50)  | 사용자 IP      | YES     | -       |
| created_at      | TIMESTAMP    | 생성 시각       | NO      | -       |

---

## API_CALL_LOG

> MSA / API Gateway / API Trace 추적용

| 컬럼명              | 데이터 타입       | 설명             | Null 허용 | PK / FK |
|------------------|--------------|----------------|---------|---------|
| api_log_id       | BIGINT       | API 로그 ID      | NO      | PK      |
| trace_id         | VARCHAR(255) | Correlation ID | NO      | -       |
| span_id          | VARCHAR(255) | Span ID        | YES     | -       |
| service_name     | VARCHAR(100) | 호출 서비스         | NO      | -       |
| api_name         | VARCHAR(255) | API 이름         | NO      | -       |
| request_uri      | VARCHAR(500) | 요청 URI         | NO      | -       |
| http_method      | VARCHAR(20)  | HTTP Method    | NO      | -       |
| request_payload  | JSON         | 요청 데이터         | YES     | -       |
| response_payload | JSON         | 응답 데이터         | YES     | -       |
| response_code    | VARCHAR(20)  | 응답 코드          | NO      | -       |
| duration_ms      | BIGINT       | 응답 시간 (ms)     | YES     | -       |
| client_ip        | VARCHAR(50)  | 클라이언트 IP       | YES     | -       |
| server_ip        | VARCHAR(50)  | 서버 IP          | YES     | -       |
| requested_at     | TIMESTAMP    | 요청 시각          | NO      | -       |
| responded_at     | TIMESTAMP    | 응답 시각          | YES     | -       |

---

## AI_USAGE_LOG

> LLM 호출 및 사용량 추적

| 컬럼명              | 데이터 타입       | 설명                    | Null 허용 | PK / FK |
|------------------|--------------|-----------------------|---------|---------|
| ai_usage_log_id  | BIGINT       | AI 로그 ID              | NO      | PK      |
| user_id          | BIGINT       | 사용자 ID                | YES     | FK      |
| session_id       | BIGINT       | AI 채팅 세션 ID           | YES     | FK      |
| model_name       | VARCHAR(100) | 사용 모델                 | NO      | -       |
| response_time_ms | BIGINT       | 응답 시간                 | YES     | -       |
| request_type     | VARCHAR(50)  | CHAT / BRIEFING / RAG | YES     | -       |
| success_yn       | BOOLEAN      | 성공 여부                 | NO      | -       |
| created_at       | TIMESTAMP    | 생성 시각                 | NO      | -       |

---

## AI_PROMPT_LOG

> AI 프롬프트 추적용

프롬프트 유형: 자산 분석 / 소비 분석 / 투자 추천 / 이상거래 탐지 / 브리핑 생성 / 요약 / 알림 생성

| 컬럼명           | 데이터 타입      | 설명         | Null 허용 | PK / FK |
|---------------|-------------|------------|---------|---------|
| prompt_log_id | BIGINT      | 프롬프트 로그 ID | NO      | PK      |
| user_id       | BIGINT      | 사용자 ID     | YES     | FK      |
| session_id    | BIGINT      | 세션 ID      | YES     | FK      |
| prompt_type   | VARCHAR(50) | 프롬프트 유형    | NO      | -       |
| system_prompt | TEXT        | 시스템 프롬프트   | YES     | -       |
| user_prompt   | TEXT        | 사용자 프롬프트   | YES     | -       |
| ai_response   | LONGTEXT    | AI 응답      | YES     | -       |
| created_at    | TIMESTAMP   | 생성 시각      | NO      | -       |

---

## AI_ACTION_LOG

> AI 이체/매수 추천 감사 로그

| 컬럼명              | 데이터 타입                                            | 설명       | Null 허용 | PK / FK |
|------------------|---------------------------------------------------|----------|---------|---------|
| ai_action_log_id | BIGINT                                            | 액션 로그 ID | NO      | PK      |
| user_id          | BIGINT                                            | 사용자 ID   | NO      | FK      |
| action_type      | ENUM('TRANSFER','BUY','SELL','AUTO_DISTRIBUTION') | 액션 유형    | NO      | -       |
| action_payload   | JSON                                              | 액션 데이터   | YES     | -       |
| approved_yn      | BOOLEAN                                           | 승인 여부    | NO      | -       |
| executed_yn      | BOOLEAN                                           | 실행 여부    | NO      | -       |
| result_message   | VARCHAR(500)                                      | 결과 메시지   | YES     | -       |
| created_at       | TIMESTAMP                                         | 생성 시각    | NO      | -       |

---

## SYSTEM_ERROR_LOG

> 전체 시스템 장애 추적

| 컬럼명             | 데이터 타입                                 | 설명          | Null 허용 | PK / FK |
|-----------------|----------------------------------------|-------------|---------|---------|
| error_log_id    | BIGINT                                 | 에러 로그 ID    | NO      | PK      |
| trace_id        | VARCHAR(255)                           | Trace ID    | YES     | -       |
| service_name    | VARCHAR(100)                           | 서비스명        | NO      | -       |
| error_level     | ENUM('INFO','WARN','ERROR','CRITICAL') | 에러 레벨       | NO      | -       |
| error_code      | VARCHAR(100)                           | 에러 코드       | YES     | -       |
| error_message   | TEXT                                   | 에러 메시지      | NO      | -       |
| stack_trace     | LONGTEXT                               | Stack Trace | YES     | -       |
| request_uri     | VARCHAR(500)                           | 요청 URI      | YES     | -       |
| request_payload | JSON                                   | 요청 데이터      | YES     | -       |
| resolved_yn     | BOOLEAN                                | 해결 여부       | NO      | -       |
| resolved_at     | TIMESTAMP                              | 해결 시각       | YES     | -       |
| created_at      | TIMESTAMP                              | 생성 시각       | NO      | -       |

---

## SECURITY_AUDIT_LOG

> 금융 보안 감사 로그

| 컬럼명             | 데이터 타입                 | 설명       | Null 허용 | PK / FK |
|-----------------|------------------------|----------|---------|---------|
| audit_log_id    | BIGINT                 | 감사 로그 ID | NO      | PK      |
| user_id         | BIGINT                 | 사용자 ID   | YES     | FK      |
| audit_type      | VARCHAR(100)           | 감사 유형    | NO      | -       |
| target_resource | VARCHAR(255)           | 접근 대상    | YES     | -       |
| access_result   | ENUM('SUCCESS','FAIL') | 접근 결과    | NO      | -       |
| ip_address      | VARCHAR(50)            | IP 주소    | YES     | -       |
| device_info     | VARCHAR(255)           | 디바이스 정보  | YES     | -       |
| created_at      | TIMESTAMP              | 생성 시각    | NO      | -       |

---

## BATCH_EXECUTION_LOG

> 스케줄러 / ETL / 분석 배치 로그

| 컬럼명              | 데이터 타입                           | 설명       | Null 허용 | PK / FK |
|------------------|----------------------------------|----------|---------|---------|
| batch_log_id     | BIGINT                           | 배치 로그 ID | NO      | PK      |
| batch_name       | VARCHAR(255)                     | 배치 이름    | NO      | -       |
| execution_status | ENUM('SUCCESS','FAIL','RUNNING') | 실행 상태    | NO      | -       |
| processed_count  | BIGINT                           | 처리 건수    | YES     | -       |
| error_count      | BIGINT                           | 실패 건수    | YES     | -       |
| started_at       | TIMESTAMP                        | 시작 시각    | NO      | -       |
| finished_at      | TIMESTAMP                        | 종료 시각    | YES     | -       |

---

## LANGGRAPH_EXECUTION_LOG

> LangGraph Agent 실행 추적

| 컬럼명               | 데이터 타입       | 설명         | Null 허용 | PK / FK |
|-------------------|--------------|------------|---------|---------|
| execution_log_id  | BIGINT       | 실행 로그 ID   | NO      | PK      |
| session_id        | BIGINT       | AI 세션 ID   | YES     | FK      |
| graph_name        | VARCHAR(100) | Graph 이름   | NO      | -       |
| node_name         | VARCHAR(100) | Node 이름    | NO      | -       |
| execution_order   | INT          | 실행 순서      | NO      | -       |
| execution_result  | VARCHAR(100) | 실행 결과      | YES     | -       |
| execution_time_ms | BIGINT       | 실행 시간 (ms) | YES     | -       |
| executed_at       | TIMESTAMP    | 실행 시각      | NO      | -       |