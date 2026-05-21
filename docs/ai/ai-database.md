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
| ANALYSIS_USER_BEHAVIOR_PATTERN | LLM | 행동 패턴 (우선순위 낮음) |
| ANALYSIS_AI_VECTOR_METADATA | 임베딩 | Vector DB 메타데이터 |

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