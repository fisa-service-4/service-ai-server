# service-backend API 명세

> Base URL: `/api/v1` | Port: `8080`

---

## AUTH API

| Method | URL                   | 설명                 | 인증     |
|--------|-----------------------|--------------------|--------|
| POST   | /auth/signup          | 회원가입               | 불필요    |
| POST   | /auth/phone/send      | 휴대폰 인증 요청          | 불필요    |
| POST   | /auth/phone/verify    | 휴대폰 인증 검증          | 불필요    |
| POST   | /auth/pin             | PIN 등록             | Bearer |
| POST   | /auth/mydata/consent  | 마이데이터 동의           | Bearer |
| POST   | /auth/signup/complete | 회원가입 완료            | Bearer |
| POST   | /auth/login           | 로그인                | 불필요    |
| POST   | /auth/logout          | 로그아웃               | Bearer |
| POST   | /auth/reissue         | 토큰 재발급             | 불필요    |
| POST   | /auth/pin/verify      | PIN 검증 (일반+거래용 통합) | Bearer |
| PATCH  | /auth/pin             | PIN 변경             | Bearer |

---

## USER API

| Method | URL               | 설명       | 인증     |
|--------|-------------------|----------|--------|
| GET    | /users/me         | 내 정보 조회  | Bearer |
| PATCH  | /users/me         | 프로필 수정   | Bearer |
| PATCH  | /users/me/consent | 알림 동의 수정 | Bearer |
| DELETE | /users/me         | 회원 탈퇴    | Bearer |

---

## MYDATA API

| Method | URL                      | 설명            | 인증     |
|--------|--------------------------|---------------|--------|
| GET    | /mydata/institutions     | 연동 가능 기관 목록   | Bearer |
| POST   | /mydata/connect          | 마이데이터 연동 실행   | Bearer |
| GET    | /mydata/status           | 연동 현황 조회 (폴링) | Bearer |
| GET    | /mydata/connections      | 연동 목록 조회      | Bearer |
| DELETE | /mydata/connections/{id} | 연동 해제         | Bearer |
| POST   | /mydata/sync             | 동기화 요청        | Bearer |

---

## NOTIFICATION API

| Method | URL                      | 설명       | 인증     |
|--------|--------------------------|----------|--------|
| GET    | /notifications           | 알림 목록 조회 | Bearer |
| PATCH  | /notifications/{id}/read | 알림 읽음 처리 | Bearer |
| PATCH  | /notifications/read-all  | 전체 읽음 처리 | Bearer |

---

## ACCOUNT API

| Method | URL                                | 설명       | 인증     |
|--------|------------------------------------|----------|--------|
| GET    | /accounts                          | 내 계좌 조회  | Bearer |
| GET    | /accounts/{accountId}              | 계좌 상세 조회 | Bearer |
| GET    | /accounts/{accountId}/balance      | 잔액 조회    | Bearer |
| GET    | /accounts/{accountId}/transactions | 거래내역 조회  | Bearer |

---

## TRANSFER API

| Method | URL                             | 설명       | 인증         |
|--------|---------------------------------|----------|------------|
| POST   | /transfers                      | 이체 요청    | Bearer+PIN |
| POST   | /transfers/{transferId}/approve | 이체 승인    | Bearer     |
| GET    | /transfers/{transferId}         | 이체 결과 조회 | Bearer     |
| POST   | /transfers/auto                 | 자동이체 실행  | Bearer     |

---

## PAYMENT MATCHING API

| Method | URL                                    | 설명       | 인증     |
|--------|----------------------------------------|----------|--------|
| GET    | /payment-matchings                     | 매칭 목록 조회 | Bearer |
| PATCH  | /payment-matchings/{matchingId}/manual | 수동 매칭 처리 | Bearer |

---

## STOCK API

| Method | URL                       | 설명        | 인증     |
|--------|---------------------------|-----------|--------|
| GET    | /stocks/search            | 종목 검색     | Bearer |
| GET    | /stocks/{stockCode}/price | 종목 현재가 조회 | Bearer |
| GET    | /stocks/{stockCode}/chart | 종목 차트 조회  | Bearer |

---

## ORDER API

| Method | URL                      | 설명       | 인증         |
|--------|--------------------------|----------|------------|
| POST   | /orders                  | 주식 주문 생성 | Bearer+PIN |
| POST   | /orders/{orderId}/cancel | 주문 취소    | Bearer+PIN |
| GET    | /orders                  | 주문 내역 조회 | Bearer     |
| GET    | /orders/{orderId}        | 주문 상세 조회 | Bearer     |

---

## EXECUTION API

| Method | URL         | 설명       | 인증     |
|--------|-------------|----------|--------|
| GET    | /executions | 체결 내역 조회 | Bearer |

---

## HOLDING API

| Method | URL               | 설명       | 인증     |
|--------|-------------------|----------|--------|
| GET    | /holdings         | 보유 종목 조회 | Bearer |
| GET    | /holdings/returns | 수익률 조회   | Bearer |

---

## PORTFOLIO API

| Method | URL        | 설명       | 인증     |
|--------|------------|----------|--------|
| GET    | /portfolio | 포트폴리오 조회 | Bearer |

---

## FAVORITE STOCK API

| Method | URL                           | 설명         | 인증     |
|--------|-------------------------------|------------|--------|
| POST   | /favorite-stocks              | 관심종목 등록    | Bearer |
| DELETE | /favorite-stocks/{favoriteId} | 관심종목 삭제    | Bearer |
| GET    | /favorite-stocks              | 관심종목 목록 조회 | Bearer |

---

## VIRTUAL SALARY API

| Method | URL                            | 설명          | 인증     |
|--------|--------------------------------|-------------|--------|
| GET    | /virtual-salary                | 가상월급 설정 조회  | Bearer |
| POST   | /virtual-salary                | 가상월급 설정 저장  | Bearer |
| GET    | /virtual-salary/recommendation | AI 추천 비율 조회 | Bearer |

---

## AI STOCKS API

| Method | URL                     | 설명          | 인증     |
|--------|-------------------------|-------------|--------|
| GET    | /ai/stocks/accounts     | 주문 가능 계좌 조회 | Bearer |
| GET    | /ai/stocks/cash-balance | 예수금 조회      | Bearer |

---

## ADMIN API

| Method | URL                          | 설명           | 인증           |
|--------|------------------------------|--------------|--------------|
| GET    | /admin/users                 | 사용자 목록 조회    | Bearer+ADMIN |
| GET    | /admin/users/{userId}        | 사용자 상세 조회    | Bearer+ADMIN |
| PATCH  | /admin/users/{userId}/status | 사용자 상태 변경    | Bearer+ADMIN |
| GET    | /admin/logs/login            | 로그인 이력 조회    | Bearer+ADMIN |
| GET    | /admin/logs/ai               | AI 사용 로그 조회  | Bearer+ADMIN |
| GET    | /admin/logs/error            | 시스템 오류 로그 조회 | Bearer+ADMIN |
| PATCH  | /admin/logs/error/{id}       | 오류 로그 해결 처리  | Bearer+ADMIN |
| GET    | /admin/logs/api              | API 호출 로그 조회 | Bearer+ADMIN |
| GET    | /admin/logs/notification     | 알림 발송 로그 조회  | Bearer+ADMIN |

---

## ADMIN MONITORING API

| Method | URL                         | 설명          | 인증           |
|--------|-----------------------------|-------------|--------------|
| GET    | /admin/monitoring/dashboard | 관리자 대시보드 조회 | Bearer+ADMIN |
| POST   | /admin/batches/run          | 배치 수동 실행    | Bearer+ADMIN |
| GET    | /admin/batches/status       | 배치 상태 조회    | Bearer+ADMIN |