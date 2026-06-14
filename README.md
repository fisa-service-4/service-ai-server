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

### 1. LLM 자유도 제한 — 고정 파이프라인 설계

일반적인 LangGraph Agent는 LLM이 자유롭게 tool을 선택·실행합니다.
금융권에서는 LLM의 hallucination으로 인한 오실행이 치명적이므로, **LLM 역할을 의도 분류와 정보 추출로만 제한**하고 금융 액션 실행 경로는 코드 레벨에서 고정했습니다.

```
[LLM 담당]                    [코드로 고정]
의도 분류 (Router)     →      Guard → 서브그래프 → Executor
정보 추출 (Extract)
```

### 2. LangGraph interrupt() 기반 PIN 인증 플로우

주문·이체 실행 전 `interrupt()`로 그래프를 일시 중단하고 PIN 입력을 대기합니다.
PIN 입력 후 `Command(resume=pin)`으로 이전 state를 완전히 복구하여 실행을 재개합니다.
PIN 검증은 Backend `/auth/pin/verify` API에 위임하여 인증 책임을 분리했습니다.

```
주문/이체 확인 메시지
        ↓
   interrupt() ← 그래프 일시 중단
        ↓ (Frontend: PIN 입력)
  Command(resume=pin)
        ↓
   verify_pin() → Backend
        ↓ (matched: true)
     Executor → 실행
```

### 3. 의도별 서브그래프 분리

ASSET / STOCK / TRANSFER를 독립 서브그래프로 분리하여 각 도메인 로직이 서로 영향을 주지 않습니다.
Guard 노드를 통해 중앙 정책 제어가 가능한 구조입니다.

### 4. RAG + 개인화 데이터 결합

pgvector 기반 Vector DB에 사용자의 개인 분석 데이터(3개월 이내)와 금융 공통 지식을 함께 저장합니다.
질문 임베딩으로 유사도 검색 후 LLM 프롬프트에 컨텍스트로 제공해 개인화된 금융 상담을 구현합니다.

### 5. 멀티턴 대화 + TTL 캐시

세션별 메시지 이력을 로컬 TTLCache(1시간)에 관리하고, `thread_version`으로 interrupt 폐기 및 재시작을 처리합니다.
interrupt 발생 시 `pre_interrupt_count`를 기록해 PIN 입력 전후 메시지를 정확히 구분합니다.

### 6. 포괄적 로깅 (비동기 백그라운드)

모든 노드에 `@log_node` 데코레이터를 적용해 실행 시간·성공/실패를 기록합니다.
LLM 프롬프트/응답, 금융 액션 이력을 별도 테이블에 저장하며, asyncio 백그라운드로 실행해 응답 지연 없이 처리합니다.

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
│   │   └── log_utils.py        # 로깅 유틸리티
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
                    Save_Memory
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
분석 결과 텍스트
    → BGE-M3 임베딩 (로컬)
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
