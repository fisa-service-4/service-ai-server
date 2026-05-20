# db-architecture.md

# Database Architecture

# DB 구성 개요

본 프로젝트는 금융 서비스 특성에 맞춰 운영 데이터, 분석 데이터, 감사 로그, 금융 원장 데이터를 분리한 구조를 사용합니다.

- 운영 성능 확보
- 분석 부하 분리
- 금융 감사 로그 보관
- 분산 트랜잭션 관리
- AI 검색 성능 최적화

를 목적으로 설계했습니다.

---

# 전체 DB 구성

| DB        | 역할                     | 위치      |
|-----------|------------------------|---------|
| 운영 DB     | 사용자 서비스 데이터            | AWS RDS |
| 분석 DB     | 통계 및 소비 분석 데이터         | AWS EC2 |
| 로그 DB     | 감사 및 접근 로그 저장          | AWS EC2 |
| Vector DB | AI 임베딩 및 RAG 검색        | AWS EC2 |
| 거래 DB     | Saga / Outbox / 이벤트 저장 | 온프레미스   |
| 은행 DB     | 계좌 및 거래 원장             | 온프레미스   |
| 카드 DB     | 카드 결제 및 소비 데이터         | 온프레미스   |
| 증권 DB     | 주문 및 체결 데이터            | 온프레미스   |

---

# 운영 DB

@db-operation-spec.md
사용자 서비스의 핵심 데이터를 저장합니다.

| 테이블명                                 | 설명          |
|--------------------------------------|-------------|
| USERS                                | 사용자 기본 정보   |
| USER_PROFILE                         | 사용자 상세 프로필  |
| PIN_AUTH                             | 간편 비밀번호 인증  |
| LINKED_FINANCIAL_ACCOUNT             | 연결 금융 계좌    |
| ACCOUNT_MAPPING                      | 계좌 목적 매핑    |
| INTEGRATED_TRANSACTION_HISTORY       | 통합 입출금 거래내역 |
| INTEGRATED_STOCK_TRANSACTION_HISTORY | 통합 주식 거래내역  |
| CONTRACT                             | 프리랜서 계약 정보  |
| CONTRACT_SETTLEMENT                  | 계약 정산 정보    |
| PAYMENT_MATCHING                     | 입금 매칭 정보    |
| VIRTUAL_SALARY_SETTING               | 가상 월급 설정    |
| FAVORITE_STOCK                       | 관심 종목       |
| AI_CHAT_SESSION                      | AI 채팅 세션    |
| AI_CHAT_MESSAGE                      | AI 채팅 메시지   |
| NOTIFICATION                         | 알림          |
| AI_BRIEFING                          | AI 브리핑      |

---

# 분석 DB

@db-analytics-spec.md
통계 및 AI 분석용 데이터를 저장합니다.

| 테이블명                           | 설명           |
|--------------------------------|--------------|
| ANALYSIS_RAW_TRANSACTION       | 원천 거래 데이터    |
| ANALYSIS_MONTHLY_INCOME        | 월 수입 분석      |
| ANALYSIS_MONTHLY_EXPENSE       | 월 지출 분석      |
| ANALYSIS_CONSUMPTION_PATTERN   | 소비 패턴 분석     |
| ANALYSIS_ASSET_SNAPSHOT        | 자산 스냅샷       |
| ANALYSIS_AI_RECOMMENDATION     | AI 추천 이력     |
| ANALYSIS_AI_VECTOR_METADATA    | RAG 벡터 메타데이터 |
| ANALYSIS_AI_BRIEFING_HISTORY   | AI 브리핑 이력    |
| ANALYSIS_USER_BEHAVIOR_PATTERN | 사용자 행동 패턴    |

---

# 로그 DB

@db-audit-spec.md

감사(Audit) 및 운영 로그 데이터를 저장합니다.

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

# Vector DB

AI 검색 증강 생성(RAG)용 벡터 데이터를 저장합니다.

## 주요 데이터

- 임베딩 벡터
- 금융 상담 문서
- FAQ
- 추천 데이터

---

# 거래 DB

@db-transaction-spec.md
분산 트랜잭션 및 이벤트 데이터를 저장합니다.

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

# 은행 DB

@db-bank-spec.md
은행 원장 데이터를 저장합니다.

| 테이블명                | 역할          |
|---------------------|-------------|
| account             | 계좌 기본 정보    |
| account_transaction | 계좌 거래 내역 원장 |
| transfer            | 이체 내역       |
| balance_snapshot    | 일별 잔액 스냅샷   |

---

# 카드 DB

@db-card-spec.md
카드 소비 데이터를 저장합니다.

| 테이블명          | 설명          |
|---------------|-------------|
| CARD_MASTER   | 카드 기본 정보    |
| CARD_APPROVAL | 카드 승인/결제 이력 |

---

# 증권 DB

@db-stock-spec.md
주식 거래 데이터를 저장합니다.

| 테이블명                       | 설명          |
|----------------------------|-------------|
| SECURITIES_ACCOUNT         | 증권 계좌 정보    |
| STOCK_MASTER               | 종목 마스터 정보   |
| STOCK_PRICE_HISTORY        | 종목 시세 이력    |
| STOCK_ORDER                | 주식 주문 정보    |
| STOCK_EXECUTION            | 주식 체결 정보    |
| STOCK_HOLDING              | 보유 종목 정보    |
| STOCK_PORTFOLIO_SNAPSHOT   | 포트폴리오 스냅샷   |
| ORDER_MODIFICATION_HISTORY | 주문 정정/취소 이력 |

---

# DB 분리 전략

## 운영/분석 분리

운영 트랜잭션 부하와 분석 쿼리 부하를 분리하기 위해 DB를 분리합니다.

---

## 금융 원장 분리

은행 및 증권 원장 데이터는 온프레미스 폐쇄망 내부에서 관리합니다.

---

## 이벤트 저장 분리

거래 이벤트 및 Saga 상태 관리를 위해 별도 거래 DB를 사용합니다.

---

# 사용 기술

| 기술         | 설명             |
|------------|----------------|
| PostgreSQL | 운영 및 분석 DB     |
| Redis      | 세션 및 캐시        |
| pgvector   | AI 벡터 검색       |
| Kafka      | 거래 이벤트 저장 및 감사 |