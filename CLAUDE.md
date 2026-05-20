# CLAUDE.md

## 1. 서비스 개요
프리랜서 특화 AI 자산관리 플랫폼
불규칙한 수입을 가진 프리랜서를 위한 통합 금융/투자 관리 서비스

**주요 기능**
- 통합 자산 조회 (은행 / 증권)
- 가상 월급 설정 및 예산 관리
- AI 기반 소비 / 투자 분석
- 마이데이터 기반 금융 데이터 수집
- 이상 거래 탐지 및 알림

---

## 2. 해당 Repository 설명

**역할**
AI 기반 자산 분석 및 리포트 생성 서버
사용자의 금융 데이터를 기반으로 소비 분석, 투자 분석, 자산 리포트 생성

**주요 기능**
- AI 채팅 / 금융 상담
- 소비 패턴 분석 리포트
- 월별 금융 리포트 생성
- 투자 성향 분석
- 분배 설정 및 AI 추천
- LangGraph Agent Workflow 관리

**Agent 노드 구성**
| 노드 | 역할 |
| --- | --- |
| Initialize | user_profile + analysis_data 로드 |
| Router | ASSET / STOCK / TRANSFER 의도 분류 |
| RAG_Consult | 금융 상담 |
| Stock_Extract | 종목/수량 추출 |
| Stock_Check | 잔액/시세 조회 |
| Transfer_Extract | 계좌/금액 추출 |
| Transfer_Check | 잔액/한도 조회 |
| Verifier | PIN 검증 대기 |
| Executor | 실제 실행 |

---

## 3. 기술 스택
| 구분 | 기술 |
| --- | --- |
| AI | Python 3.11, FastAPI, LangGraph, LangChain |
| LLM | Qwen3-8B (Ollama), BGE-M3 |
| DB | PostgreSQL 16, pgvector, Redis 7.2 |
| Infra | Docker, Docker Compose |

---

## 4. 폴더 구조
```
src/
├── agent/
│   ├── nodes/        LangGraph 노드
│   ├── tools/        외부 API 호출 도구
│   ├── state.py      ChatAgentState 정의
│   └── graph.py      LangGraph 그래프 구성
├── pipeline/         분석 배치 파이프라인
├── api/              FastAPI 엔드포인트
└── main.py
```

---

## 5. 개발 규칙

**코드 스타일**
- SonarLint 경고 제거 후 커밋
- Layered Architecture 준수
- 네이밍: 클래스 PascalCase / 메서드 camelCase / 상수 UPPER_SNAKE_CASE

**API / DB**
- 모든 응답은 공통 Response 포맷 사용
- Swagger 문서 작성 필수
- 에러 코드는 error-code.md 기준 사용
- created_at / updated_at 기본 포함
- DB 변경 시 md 문서 수정 필수

**이벤트**
- 이벤트 스키마 변경 시 전체 서버 영향도 확인
- Kafka Consumer 멱등성 보장

---

## 6. 절대 하지 말 것

**Git**
- main / develop 직접 push 금지
- force push 금지
- 리뷰 없이 merge 금지

**보안**
- API Key 하드코딩 금지
- .env 커밋 금지
- 개인정보 로그 출력 금지
- 금융 데이터 평문 저장 금지

**코드**
- print() 커밋 금지
- TODO 남긴 채 merge 금지

---

## 7. 참조 문서
| 파일 | 언제 참조 |
| --- | --- |
| @docs/architecture-index.md | 시스템 구조 파악할 때 |
| @docs/api/api-index.md | API 개발 시 |
| @docs/db/db-index.md | DB 작업 시 |
| @docs/convention/git-convention.md | 브랜치/커밋/PR 규칙 확인할 때 |
| @docs/tech-stack/tech-stack.md | 기술 스택 확인할 때 |