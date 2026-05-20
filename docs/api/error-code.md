# 에러 코드 정의서

> 팀 프로젝트 공통 API 에러 코드 레퍼런스
 
---

## 공통 에러 응답 포맷

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "에러 메시지"
  },
  "meta": {
    "traceId": "uuid"
  },
  "timestamp": "2026-05-17T12:00:00"
}
```

 
---

## AUTH / USER / MYDATA ERROR

| 코드               | HTTP Status | 설명              |
|------------------|-------------|-----------------|
| VALID_001        | 400         | 입력값 오류          |
| VALID_002        | 400         | 필수값 누락          |
| AUTH_001         | 401         | JWT 인증 실패       |
| AUTH_002         | 401         | AccessToken 만료  |
| AUTH_003         | 401         | RefreshToken 만료 |
| AUTH_004         | 401         | 로그인 실패          |
| AUTH_005         | 409         | 이미 가입된 이메일      |
| AUTH_006         | 400         | 비밀번호 형식 오류      |
| AUTH_007         | 400         | 휴대폰 인증 실패       |
| AUTH_008         | 400         | 인증번호 불일치        |
| AUTH_009         | 400         | 인증번호 만료         |
| AUTH_010         | 403         | 접근 권한 없음        |
| PIN_001          | 400         | PIN 미설정         |
| PIN_002          | 400         | PIN 잠금          |
| PIN_003          | 400         | PIN 불일치         |
| USER_001         | 404         | 사용자 없음          |
| MYDATA_001       | 404         | 연동 기관 없음        |
| MYDATA_002       | 409         | 이미 연동된 기관       |
| MYDATA_003       | 500         | 마이데이터 연동 실패     |
| MYDATA_004       | 404         | 연동 정보 없음        |
| NOTIFICATION_001 | 404         | 알림 없음           |

 
---

## ACCOUNT / TRANSFER ERROR

| 코드              | HTTP Status | 설명          |
|-----------------|-------------|-------------|
| ACCOUNT_001     | 404         | 계좌 없음       |
| ACCOUNT_002     | 403         | 계좌 접근 권한 없음 |
| TRANSACTION_001 | 404         | 거래내역 없음     |
| TRANSFER_001    | 400         | 이체 정보 부족    |
| TRANSFER_002    | 400         | 잔액 부족       |
| TRANSFER_003    | 404         | 수신 계좌 없음    |
| TRANSFER_004    | 500         | 이체 실행 실패    |
| TRANSFER_005    | 409         | 중복 이체 요청    |
| MATCHING_001    | 404         | 매칭 데이터 없음   |

 
---

## STOCK / ORDER ERROR

| 코드                 | HTTP Status | 설명           |
|--------------------|-------------|--------------|
| STOCK_001          | 404         | 종목 없음        |
| STOCK_002          | 500         | 현재가 조회 실패    |
| STOCK_003          | 500         | 차트 데이터 조회 실패 |
| ORDER_001          | 400         | 주문 가능 금액 부족  |
| ORDER_002          | 400         | 보유 수량 부족     |
| ORDER_003          | 404         | 주문 정보 없음     |
| ORDER_004          | 400         | 주문 상태 오류     |
| ORDER_005          | 500         | 주문 실행 실패     |
| EXECUTION_001      | 404         | 체결 내역 없음     |
| HOLDING_001        | 404         | 보유 종목 없음     |
| FAVORITE_001       | 404         | 관심종목 없음      |
| VIRTUAL_SALARY_001 | 400         | 비율 합계 오류     |

 
---

## AI / ANALYSIS ERROR

| 코드                 | HTTP Status | 설명             |
|--------------------|-------------|----------------|
| CHAT_001           | 500         | 채팅 세션 생성 실패    |
| CHAT_002           | 404         | 채팅 세션 없음       |
| AI_001             | 500         | AI 응답 생성 실패    |
| AI_002             | 504         | LLM 응답 Timeout |
| AI_003             | 500         | AI 실행 실패       |
| DISTRIBUTION_001   | 500         | AI 분배 추천 생성 실패 |
| DISTRIBUTION_002   | 500         | 분배 설정 저장 실패    |
| ACTION_001         | 404         | 실행 상태 정보 없음    |
| ANALYSIS_001       | 404         | 소비 분석 데이터 없음   |
| ANALYSIS_002       | 404         | 수입 분석 데이터 없음   |
| ANALYSIS_003       | 404         | 자산 분석 데이터 없음   |
| ANALYSIS_004       | 404         | 소비 패턴 데이터 없음   |
| ANALYSIS_005       | 404         | 추천 데이터 없음      |
| ANALYSIS_006       | 500         | 분석 배치 실행 실패    |
| BRIEFING_001       | 500         | 브리핑 생성 실패      |
| BRIEFING_002       | 500         | 브리핑 저장 실패      |
| RECOMMENDATION_001 | 500         | 추천 생성 실패       |

 
---