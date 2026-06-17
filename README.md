# service-ai-server

프리랜서 특화 AI 자산관리 플랫폼의 AI 서버입니다.
사용자의 금융 데이터를 기반으로 소비 분석, 투자 상담, 주식 주문, 이체 실행 등 AI 기반 금융 서비스를 제공합니다.

---

## 목차

- [서비스 개요](#서비스-개요)
- [기술 스택](#기술-스택)
- [아키텍처](#아키텍처)
- [주요 기능](#주요-기능)
- [프로젝트 구조](#프로젝트-구조)
- [LangGraph 그래프 구조](#langgraph-그래프-구조)
- [API 명세](#api-명세)
- [분석 파이프라인](#분석-파이프라인)
- [환경 변수](#환경-변수)
- [실행 방법](#실행-방법)

---

## 서비스 개요

불규칙한 수입을 가진 프리랜서를 위한 AI 금융 어시스턴트입니다.

| 기능 | 설명 |
|------|------|
| AI 금융 상담 | RAG 기반 개인화 소비·투자 분석 상담 |
| 주식 주문 | 종목 검색, 시세 조회, 매수/매도 주문 실행 |
| 계좌 이체 | 계좌 조회, 잔액 확인, 이체 실행 |
| 분배 설정 | AI 추천 기반 가상월급 자동 분배 설정 |
| 분석 파이프라인 | 거래 데이터 → 통계 집계 → LLM 분석 → Vector DB 저장 |

---

## 기술 스택

| 구분 | 기술 |
|------|------|
| Language | Python 3.11 |
| Framework | FastAPI |
| AI Orchestration | LangGraph |
| LLM | Qwen3-8B (Ollama) |
| Embedding | BGE-M3 (로컬) |
| Vector DB | PostgreSQL 16 + pgvector |
| Analytics DB | PostgreSQL 16 |
| Log DB | PostgreSQL 16 |
| HTTP Client | httpx (비동기) |
| Cache | cachetools TTLCache |
| Auth | PyJWT |

---

## 아키텍처

```
Frontend (Next.js)
      ↕ HTTP
service-backend (Spring Boot :8080)  ←→  service-ai-server (FastAPI :8000)
      ↕
  운영 DB (PostgreSQL)

service-ai-server
      ↕ (주식 시세/종목 검색만)
transaction-server (:8083)
```

### 통신 원칙

- AI 서버는 **Frontend와 직접 연결하지 않습니다.**
- AI 서버는 **운영 DB에 직접 접근하지 않습니다.**
- 계좌·잔액·주문·이체·메시지 저장 등 모든 금융 데이터는 **Backend API를 경유**합니다.
- PIN 검증과 토큰 인증은 **Backend에 위임**하여 단일 인증 책임 원칙을 준수합니다.
- 주식 시세·종목 검색은 실시간성을 위해 **Transaction 서버에 직접 조회**합니다.

---

## 주요 기능

### 1. 고정 파이프라인 설계 — LLM 역할 최소화

LLM이 자유롭게 도구를 선택·실행하는 일반적인 Agent 방식은 금융 실행 오류 시 치명적입니다. 이 서버는 **LLM 역할을 의도 분류(Router)와 정보 추출(Extract)로만 한정**하고, 금융 액션의 실행 경로는 코드 레벨에서 고정해 hallucination이 실제 금융 거래에 영향을 줄 수 없도록 설계했습니다.

```
[LLM]                       [코드 고정]
Router (의도 분류)    →     Guard → 서브그래프 선택
Extract (정보 추출)   →     Verifier → Executor
```

### 2. LangGraph interrupt() 기반 PIN 인증

주문·이체·분배 설정 실행 직전 Verifier 노드에서 `interrupt()`로 그래프를 일시 중단합니다. 직전 노드(Stock_Check / Transfer_Check / Asset_Action)가 생성한 거래 확인 메시지를 interrupt value로 전달해 Frontend가 PIN 입력 UI를 표시하고, 사용자가 PIN을 입력하면 `Command(resume=pin)`으로 이전 State를 완전히 복구해 실행을 재개합니다. PIN 검증은 Backend `/auth/pin/verify` API에 위임해 인증 책임을 분리했습니다.

```
Stock_Check / Transfer_Check / Asset_Action
        ↓ (거래 확인 메시지 생성)
   interrupt(confirm_msg) ← 그래프 일시 중단
        ↓ (Frontend: PIN 입력)
  Command(resume=pin)
        ↓
   verify_pin() → Backend /auth/pin/verify
        ↓ (matched: true)
     Executor → 금융 액션 실행
```

### 3. 의도별 서브그래프 분리

사용자 입력을 ASSET / STOCK / TRANSFER 세 도메인으로 분류하고 각각 독립 서브그래프로 처리합니다. 도메인 간 로직이 서로 영향을 주지 않으며, Guard 노드가 금융 정책을 중앙에서 검사해 세 서브그래프 모두에 일관되게 적용합니다.

| 서브그래프 | 주요 역할 |
|------------|---------|
| Asset_Flow | 자산 현황 조회, RAG 기반 금융 상담, 분배 설정 적용 |
| Stock_Flow | 종목·수량 추출, 시세 조회, 매수/매도 주문 실행 |
| Transfer_Flow | 계좌·금액 추출, 잔액 확인, 계좌 이체 실행 |

### 4. 개인화 컨텍스트 사전 로드 + RAG 결합

Initialize 노드가 매 대화 시작 시 Analytics DB에서 **월별 수입/지출 통계, 소비 패턴, 자산 스냅샷**을 로드해 State에 미리 담아둡니다. RAG_Consult 노드는 pgvector 유사도 검색(LLM 합성 인사이트 + 금융 공통 지식)과 DB 직접 쿼리(AI 추천값)를 병렬로 조회해 LLM 프롬프트를 구성합니다.

- **Vector DB**: 파이프라인이 사전 생성한 LLM 합성 인사이트 2개 (소비 성향 종합 / 개선 포인트) — 시맨틱 검색에 활용
- **Analytics DB 직접 쿼리**: AI 추천값 (가상월급·투자·비상금 금액) — 정확한 수치 보장

```
[Vector DB] 유사도 검색 — LLM 합성 인사이트 + 금융 공통 지식
[Analytics DB] 직접 쿼리 — AI 추천값 (SALARY/INVESTMENT/EMERGENCY)
        ↓ RAG_Consult 노드 (병렬 조회)
    LLM 프롬프트 (개인화 컨텍스트 포함)
```

### 5. 멀티턴 대화 — interrupt 폐기 처리

세션별 메시지 이력을 로컬 TTLCache(1시간)로 관리합니다. interrupt 대기 중 사용자가 새 메시지를 보내면 기존 interrupt 스냅샷을 MemorySaver에서 삭제하고 `thread_version`을 증가시켜 새 스레드로 재시작합니다. `pre_interrupt_count`로 interrupt 이전 메시지 경계를 기록해 재시작 시 이력이 정확히 잘립니다.

### 6. 비동기 백그라운드 로깅

모든 노드에 `@log_node` 데코레이터를 적용해 실행 시간·성공/실패를 기록합니다. LLM 프롬프트/응답, 금융 액션 이력도 별도 테이블에 저장하며, `asyncio.create_task()`로 백그라운드 처리해 로깅이 응답 지연에 영향을 주지 않습니다.

| 테이블 | 저장 내용 |
|--------|---------|
| `langgraph_execution_log` | 노드별 실행 시간, 성공/실패 |
| `ai_prompt_log` | LLM 프롬프트 및 응답 전문 |
| `ai_action_log` | 금융 액션 실행 이력 (BUY/SELL/TRANSFER/AUTO_DISTRIBUTION) |

---

## 프로젝트 구조

```
src/
├── agent/
│   ├── nodes/                  # LangGraph 노드
│   │   ├── initialize.py       # 분석 데이터 로드 및 State 초기화
│   │   ├── router.py           # 의도 분류 (ASSET/STOCK/TRANSFER/UNKNOWN)
│   │   ├── guard.py            # 금융 정책 검사
│   │   ├── stock_extract.py    # 주식 정보 추출 (LLM)
│   │   ├── stock_check.py      # 시세·잔액 조회 및 주문 확인
│   │   ├── transfer_extract.py # 이체 정보 추출 (LLM)
│   │   ├── transfer_check.py   # 계좌·잔액 확인 및 이체 확인
│   │   ├── asset_action.py     # 자산 액션 분류 및 추천 데이터 로드
│   │   ├── rag_consult.py      # RAG 기반 금융 상담
│   │   ├── verifier.py         # PIN 인증 (interrupt)
│   │   ├── executor.py         # 금융 액션 실행
│   │   └── log_utils.py        # 노드 실행 로깅 데코레이터
│   ├── subgraphs/              # 의도별 서브그래프
│   │   ├── asset_graph.py
│   │   ├── stock_graph.py
│   │   └── transfer_graph.py
│   ├── tools/                  # 외부 API 호출 도구
│   │   ├── client.py           # HTTP 클라이언트 (Backend/Transaction)
│   │   ├── stock.py            # 주식 API
│   │   ├── transfer.py         # 이체 API
│   │   ├── asset.py            # 자산 API
│   │   ├── auth.py             # 인증 API
│   │   └── rag.py              # Vector DB 검색
│   ├── graph.py                # 메인 LangGraph 그래프
│   ├── state.py                # ChatAgentState 정의
│   └── llm.py                  # LLM 클라이언트
├── pipeline/                   # 분석 배치 파이프라인
│   ├── runner.py               # 파이프라인 실행기
│   ├── db.py                   # DB 연결 풀
│   └── steps/
│       ├── stat_analysis.py    # 통계 집계
│       ├── llm_analysis.py     # LLM 분석
│       └── embedding.py        # 임베딩 및 Vector DB 저장
├── api/
│   ├── chat.py                 # 채팅 엔드포인트
│   └── response.py             # 공통 응답 포맷
└── main.py                     # FastAPI 앱 진입점
```

---

## LangGraph 그래프 구조

### 메인 그래프

```
[START]
   ↓
Initialize → Router → Guard
                         ↓
          ┌──────────────┼──────────────┐
       ASSET           STOCK        TRANSFER
          ↓              ↓              ↓
     Asset_Flow     Stock_Flow   Transfer_Flow
          └──────────────┴──────────────┘
                         ↓
                       [END]
```

### Stock_Flow 서브그래프

```
Stock_Extract → Stock_Check
                     ↓
        ┌────────────┼────────────┐
      조회완료     주문준비     정보부족
        ↓           ↓            ↓
       END       Verifier  Stock_Extract
                    ↓ (PIN 성공)
                 Executor → END
```

### Transfer_Flow 서브그래프

```
Transfer_Extract → Transfer_Check
                        ↓
               ┌────────┴────────┐
           정보완료           정보부족
               ↓                ↓
           Verifier            END
               ↓ (PIN 성공)
            Executor → END
```

### Asset_Flow 서브그래프

```
Asset_Action
     ↓
┌────┴──────────┬──────────────┐
pending_action  consult        기타
     ↓            ↓             ↓
 Verifier     RAG_Consult      END
     ↓ (PIN 성공)
  Executor → END
```

---

## API 명세

### 채팅

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | `/api/v1/ai/chat/run` | 메시지 전송 및 AI 응답 |

**Request Body**
```json
{
  "sessionId": 123,
  "message": "삼성전자 10주 매수해줘",
  "isPin": false,
  "accountId": 2001
}
```

**Response**
```json
{
  "success": true,
  "data": {
    "role": "AI",
    "intent": "STOCK",
    "content": "💰 주문 확인\n• 종목: 삼성전자\n...\nPIN을 입력해 주세요.",
    "actionRequired": true,
    "requirePin": true
  }
}
```

### 기타

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/health` | 헬스 체크 |
| GET | `/api/v1/ai/health` | AI 서비스 헬스 체크 |
| POST | `/api/v1/ai/admin/pipeline/run` | 분석 파이프라인 수동 실행 |
| POST | `/api/v1/ai/virtual-salary/recommend` | 가상월급 AI 추천 조회 |

---

## 분석 파이프라인

사용자의 거래 데이터를 분석하여 채팅 시점에 즉시 활용 가능한 개인화 데이터를 사전 생성합니다.

```
[Step 1] stat_analysis
거래 원본 데이터(analysis_raw_transaction)
    → 월별 수입/지출 통계 집계
    → analysis_monthly_income, analysis_monthly_expense 저장

[Step 2] llm_analysis
월별 통계 데이터
    → LLM 소비 패턴 분류 (consumption_type, risk_score)
    → LLM 월별 금융 브리핑 생성
    → LLM 분배 추천 생성 (SALARY/INVESTMENT/EMERGENCY)
    → analysis_consumption_pattern, ai_briefing_history, ai_recommendation 저장

[Step 3] embedding
Step 2 분석 결과 (소비 패턴 + 브리핑 + 추천)
    → LLM 인사이트 합성
        - INSIGHT_PATTERN: 소비 성향 및 재무 상태 종합 해석
        - INSIGHT_ACTION: 현재 집중해야 할 재무 개선 포인트
    → BGE-M3 임베딩 (text → vector)
    → analysis_ai_vector_metadata 저장 (pgvector)
    → 3개월 이상 된 데이터 자동 삭제
```

---

## 환경 변수

`.env` 파일을 프로젝트 루트에 생성하세요.

```env
# LLM (Ollama)
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=qwen3:8b

# 서비스 연동
BACKEND_URL=http://localhost:8080
TRANSACTION_URL=http://localhost:8083

# Analytics DB
ANALYTICS_DB_HOST=localhost
ANALYTICS_DB_PORT=5433
ANALYTICS_DB_NAME=finance_analytics
ANALYTICS_DB_USER=postgres
ANALYTICS_DB_PASSWORD=postgres

# Vector DB
VECTOR_DB_HOST=localhost
VECTOR_DB_PORT=5435
VECTOR_DB_NAME=finance_vector
VECTOR_DB_USER=postgres
VECTOR_DB_PASSWORD=postgres

# Log DB
LOG_DB_HOST=localhost
LOG_DB_PORT=5434
LOG_DB_NAME=finance_log
LOG_DB_USER=postgres
LOG_DB_PASSWORD=postgres
```

---

## 실행 방법

### 로컬 실행

```bash
# 의존성 설치
pip install -r requirements.txt

# 서버 실행
uvicorn src.main:app --reload --port 8000
```

### Docker

```bash
docker-compose up -d
```
