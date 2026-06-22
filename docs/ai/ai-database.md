# AI Database

## 분석 DB 테이블
| 테이블 | 단계 | 설명 |
| --- | --- | --- |
| ANALYSIS_RAW_TRANSACTION | 분석 전 | 원천 거래 데이터 |
| ANALYSIS_ASSET_SNAPSHOT | 분석 전 | 자산 스냅샷 |
| ANALYSIS_MONTHLY_INCOME | Python 통계 | 월 수입 분석 |
| ANALYSIS_MONTHLY_EXPENSE | Python 통계 | 월 지출 분석 |
| ANALYSIS_CONSUMPTION_PATTERN | LLM | 소비 성향 분석 |
| ANALYSIS_AI_BRIEFING_HISTORY | LLM | 브리핑 이력 |
| ANALYSIS_AI_RECOMMENDATION | LLM | AI 추천 (적용 시 applied_yn 업데이트) |

---

## Vector DB 테이블

| 테이블 | 설명 |
| --- | --- |
| ANALYSIS_AI_VECTOR_METADATA | 사용자 개인 분석 데이터 임베딩 |
| COMMON_KNOWLEDGE | 공통 금융 지식 임베딩 |

### ANALYSIS_AI_VECTOR_METADATA
| 컬럼 | 타입 | 설명 |
| --- | --- | --- |
| id | BIGSERIAL | PK |
| user_id | BIGINT | 사용자 ID |
| vector_type | VARCHAR(50) | 벡터 유형 |
| reference_id | BIGINT | 원본 데이터 ID |
| embedding_version | VARCHAR(50) | 임베딩 버전 |
| chunk_text | TEXT | 벡터 원문 |
| vector_key | VARCHAR(255) | 벡터 저장 키 (UNIQUE) |
| embedding | vector(1024) | pgvector 임베딩 |
| indexed_at | TIMESTAMP | 인덱싱 시각 |

### COMMON_KNOWLEDGE
| 컬럼 | 타입 | 설명 |
| --- | --- | --- |
| id | BIGSERIAL | PK |
| category | VARCHAR(100) | 지식 카테고리 |
| title | VARCHAR(255) | 제목 |
| chunk_text | TEXT | 내용 |
| embedding | vector(1024) | pgvector 임베딩 |
| embedding_version | VARCHAR(50) | 임베딩 버전 |
| created_at | TIMESTAMP | 생성 시각 |

---

## 채팅 세션 테이블

### AI_CHAT_SESSION
| 컬럼 | 타입 | 설명 |
| --- | --- | --- |
| session_id | BIGINT | 세션 ID (PK) |
| user_id | BIGINT | 사용자 ID (FK) |
| session_type | ENUM | CHAT / TRANSFER / STOCK / ANALYSIS |
| updated_at | TIMESTAMP | 최종 수정 시각 |

### AI_CHAT_MESSAGE
| 컬럼 | 타입 | 설명 |
| --- | --- | --- |
| message_id | BIGINT | 메시지 ID (PK) |
| session_id | BIGINT | 세션 ID (FK) |
| role | ENUM | USER / AI / SYSTEM |
| content | TEXT | 메시지 내용 |
| action_type | VARCHAR(50) | 금융 액션 유형 |
| action_confirmed_yn | BOOLEAN | 사용자 승인 여부 |
| created_at | TIMESTAMP | 생성 시각 |

---

## 세션 관리
```
session_id + user_id 기반 메모리 관리
개인정보 마스킹 로직 처리 필수
```