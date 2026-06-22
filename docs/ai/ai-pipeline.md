# AI Pipeline

## 전체 흐름
```
매일 자정 (배치)

1단계. 마이데이터 수집
마이데이터 API → mydata-server → 운영 DB

2단계. 운영 DB → 분석 DB 동기화 (1차 가공)
운영 DB → Outbox + Batch ETL → 분석 DB 분석 전 테이블
→ ANALYSIS_RAW_TRANSACTION   원천 거래 데이터
→ ANALYSIS_ASSET_SNAPSHOT    자산 스냅샷

3단계. Python Pipeline (통계 분석)
분석 전 테이블 → Python 통계 분석 → 분석 DB 저장
→ ANALYSIS_MONTHLY_INCOME    카테고리별 수입 금액
→ ANALYSIS_MONTHLY_EXPENSE   카테고리별 지출 금액

4단계. LLM 분석/요약
통계 결과 → LLM 직접 호출 → 분석 DB 저장
→ ANALYSIS_CONSUMPTION_PATTERN   소비 성향 + 위험도 + 요약
→ ANALYSIS_AI_BRIEFING_HISTORY   주간/월간 브리핑
→ ANALYSIS_AI_RECOMMENDATION     맞춤 추천

5단계. Vector DB 업데이트
LLM 결과 → BGE-M3 임베딩 → Vector DB 저장
→ ANALYSIS_AI_VECTOR_METADATA    임베딩 메타데이터
```

---

## 배치 주기
```
매일:  마이데이터 수집 → 운영 DB → 분석 DB 동기화
주간:  주간 소비패턴 + 카테고리 + 전주 비교 + 자산변화
월간:  소비/자산/수입 분석 + 사용자 프로파일링
```

---

## 데이터 흐름 상세
```
분석 전 테이블 (원천)
ANALYSIS_RAW_TRANSACTION
ANALYSIS_ASSET_SNAPSHOT
    ↓ Python 통계
분석 후 테이블 (통계)
ANALYSIS_MONTHLY_INCOME
ANALYSIS_MONTHLY_EXPENSE
    ↓ LLM 직접 호출
분석 후 테이블 (LLM)
ANALYSIS_CONSUMPTION_PATTERN
ANALYSIS_AI_BRIEFING_HISTORY
ANALYSIS_AI_RECOMMENDATION
    ↓ BGE-M3 임베딩
Vector DB
ANALYSIS_AI_VECTOR_METADATA
```