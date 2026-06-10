# db-operation-spec.md

# Operation DB 명세서

운영 DB는 사용자 서비스의 핵심 비즈니스 데이터를 관리합니다.

회원, 인증, 계약, 마이데이터 연동, 통합 거래내역,
AI 채팅, 알림, 가상 월급 등의 데이터를 저장합니다. :contentReference[oaicite:0]{index=0}

---

## 테이블 목록

| 테이블명                             | 설명                 |
| ------------------------------------ | -------------------- |
| USERS                                | 사용자 기본 정보     |
| USER_PROFILE                         | 사용자 상세 프로필   |
| PIN_AUTH                             | 간편 비밀번호 인증   |
| LINKED_FINANCIAL_ACCOUNT             | 연결 금융 계좌       |
| ACCOUNT_MAPPING                      | 계좌 목적 매핑       |
| INTEGRATED_TRANSACTION_HISTORY       | 통합 입출금 거래내역 |
| INTEGRATED_STOCK_TRANSACTION_HISTORY | 통합 주식 거래내역   |
| CONTRACT                             | 프리랜서 계약 정보   |
| CONTRACT_SETTLEMENT                  | 계약 정산 정보       |
| PAYMENT_MATCHING                     | 입금 매칭 정보       |
| VIRTUAL_SALARY_SETTING               | 가상 월급 설정       |
| FAVORITE_STOCK                       | 관심 종목            |
| AI_CHAT_SESSION                      | AI 채팅 세션         |
| AI_CHAT_MESSAGE                      | AI 채팅 메시지       |
| NOTIFICATION                         | 알림                 |
| AI_BRIEFING                          | AI 브리핑            |

---

## USERS

> 사용자 기본 정보를 저장합니다.

| 컬럼명                  | 데이터 타입  | 설명                 | Null 허용 | PK / FK |
| ----------------------- | ------------ | -------------------- | --------- | ------- |
| user_id                 | BIGINT       | 사용자 ID            | NO        | PK      |
| firebase_uid            | VARCHAR(255) | Firebase UID         | NO        | UNIQUE  |
| email                   | VARCHAR(255) | 이메일               | NO        | UNIQUE  |
| password_hash           | VARCHAR(255) | 비밀번호 해시        | NO        | -       |
| user_name               | VARCHAR(100) | 사용자명             | NO        | -       |
| phone_number            | VARCHAR(20)  | 전화번호             | NO        | UNIQUE  |
| role                    | ENUM         | 권한                 | NO        | -       |
| status                  | ENUM         | 사용자 상태          | NO        | -       |
| notification_consent_yn | BOOLEAN      | 알림 수신 동의 여부  | NO        | -       |
| terms_consent_yn        | BOOLEAN      | 약관 동의 여부       | NO        | -       |
| mydata_consent_yn       | BOOLEAN      | 마이데이터 동의 여부 | NO        | -       |
| created_at              | TIMESTAMP    | 가입일               | NO        | -       |

### role

| 값    | 설명        |
| ----- | ----------- |
| USER  | 일반 사용자 |
| ADMIN | 관리자      |

### status

| 값       | 설명   |
| -------- | ------ |
| ACTIVE   | 활성   |
| INACTIVE | 비활성 |
| WITHDRAW | 탈퇴   |
| LOCKED   | 잠금   |

---

## USER_PROFILE

> 사용자 상세 프로필 정보를 저장합니다.

| 컬럼명        | 데이터 타입  | 설명          | Null 허용 | PK / FK |
| ------------- | ------------ | ------------- | --------- | ------- |
| user_id       | BIGINT       | 사용자 ID     | NO        | PK, FK  |
| freelancer_yn | BOOLEAN      | 프리랜서 여부 | NO        | -       |
| job_type      | VARCHAR(100) | 직업 유형     | YES       | -       |

---

## PIN_AUTH

> 간편 비밀번호(PIN) 인증 정보를 저장합니다.

| 컬럼명         | 데이터 타입  | 설명       | Null 허용 | PK / FK |
| -------------- | ------------ | ---------- | --------- | ------- |
| user_id        | BIGINT       | 사용자 ID  | NO        | PK, FK  |
| pin_hash       | VARCHAR(255) | PIN 해시값 | NO        | -       |
| fail_count     | INT          | 실패 횟수  | NO        | -       |
| locked_yn      | BOOLEAN      | 잠금 여부  | NO        | -       |
| locked_at      | TIMESTAMP    | 잠금 시각  | YES       | -       |
| pin_changed_at | TIMESTAMP    | PIN 변경일 | YES       | -       |

---

## LINKED_FINANCIAL_ACCOUNT

> 연결 금융 계좌 정보를 저장합니다.

| 컬럼명              | 데이터 타입  | 설명            | Null 허용 | PK / FK |
| ------------------- | ------------ | --------------- | --------- | ------- |
| linked_account_id   | BIGINT       | 연결 계좌 ID    | NO        | PK      |
| user_id             | BIGINT       | 사용자 ID       | NO        | FK      |
| institution_type    | ENUM         | 금융기관 유형   | NO        | -       |
| institution_code    | VARCHAR(30)  | 금융기관 코드   | NO        | -       |
| external_account_id | BIGINT       | 외부 계좌 ID    | NO        | -       |
| account_masking     | VARCHAR(100) | 마스킹 계좌번호 | NO        | -       |
| synced_at           | TIMESTAMP    | 동기화 시각     | YES       | -       |

### institution_type

| 값         | 설명 |
| ---------- | ---- |
| BANK       | 은행 |
| SECURITIES | 증권 |
| CARD       | 카드 |

---

## ACCOUNT_MAPPING

> 연결 계좌의 목적 정보를 저장합니다.

| 컬럼명            | 데이터 타입 | 설명           | Null 허용 | PK / FK |
| ----------------- | ----------- | -------------- | --------- | ------- |
| mapping_id        | BIGINT      | 매핑 ID        | NO        | PK      |
| user_id           | BIGINT      | 사용자 ID      | NO        | -       |
| linked_account_id | BIGINT      | 연결 계좌 ID   | NO        | FK      |
| mapping_type      | ENUM        | 계좌 목적 유형 | NO        | -       |

### mapping_type

| 값        | 설명        |
| --------- | ----------- |
| INCOME    | 수입 관리   |
| SALARY    | 월급 관리   |
| STOCK     | 투자 관리   |
| EMERGENCY | 비상금 관리 |

---

## INTEGRATED_TRANSACTION_HISTORY

> 통합 입출금 거래내역을 저장합니다.

| 컬럼명                    | 데이터 타입   | 설명           | Null 허용 | PK / FK |
| ------------------------- | ------------- | -------------- | --------- | ------- |
| integrated_transaction_id | BIGINT        | 통합 거래 ID   | NO        | PK      |
| user_id                   | BIGINT        | 사용자 ID      | NO        | FK      |
| linked_account_id         | BIGINT        | 연결 계좌 ID   | YES       | FK      |
| institution_type          | ENUM          | 금융기관 유형  | NO        | -       |
| transaction_type          | ENUM          | 거래 유형      | NO        | -       |
| transaction_category      | VARCHAR(100)  | 거래 카테고리  | YES       | -       |
| transaction_amount        | DECIMAL(18,2) | 거래 금액      | NO        | -       |
| balance_after             | DECIMAL(18,2) | 거래 후 잔액   | YES       | -       |
| merchant_name             | VARCHAR(255)  | 가맹점명       | YES       | -       |
| original_transaction_id   | BIGINT        | 원본 거래 ID   | NO        | -       |
| transaction_occurred_at   | TIMESTAMP     | 거래 발생 시각 | NO        | -       |
| synced_at                 | TIMESTAMP     | 동기화 시각    | NO        | -       |

### institution_type

| 값   | 설명 |
| ---- | ---- |
| BANK | 은행 |
| CARD | 카드 |

### transaction_type

| 값      | 설명 |
| ------- | ---- |
| INCOME  | 수입 |
| EXPENSE | 지출 |

---

## INTEGRATED_STOCK_TRANSACTION_HISTORY

> 통합 주식 거래내역을 저장합니다.

| 컬럼명                          | 데이터 타입   | 설명              | Null 허용 | PK / FK |
| ------------------------------- | ------------- | ----------------- | --------- | ------- |
| integrated_stock_transaction_id | BIGINT        | 통합 주식 거래 ID | NO        | PK      |
| user_id                         | BIGINT        | 사용자 ID         | NO        | FK      |
| linked_account_id               | BIGINT        | 연결 계좌 ID      | NO        | FK      |
| stock_code                      | VARCHAR(20)   | 종목 코드         | NO        | -       |
| stock_name                      | VARCHAR(255)  | 종목명            | NO        | -       |
| transaction_type                | ENUM          | 거래 유형         | NO        | -       |
| transaction_quantity            | INT           | 거래 수량         | NO        | -       |
| transaction_unit_price          | DECIMAL(18,2) | 거래 단가         | NO        | -       |
| transaction_total_amount        | DECIMAL(18,2) | 총 거래 금액      | NO        | -       |
| cash_balance_after              | DECIMAL(18,2) | 거래 후 예수금    | YES       | -       |
| holding_quantity_after          | INT           | 거래 후 보유 수량 | YES       | -       |
| average_purchase_price          | DECIMAL(18,2) | 평균 매입가       | YES       | -       |
| realized_profit                 | DECIMAL(18,2) | 실현 손익         | YES       | -       |
| realized_profit_rate            | DECIMAL(5,2)  | 실현 수익률       | YES       | -       |
| original_execution_id           | BIGINT        | 원본 체결 ID      | NO        | -       |
| transaction_occurred_at         | TIMESTAMP     | 거래 발생 시각    | NO        | -       |
| synced_at                       | TIMESTAMP     | 동기화 시각       | NO        | -       |

### transaction_type

| 값   | 설명 |
| ---- | ---- |
| BUY  | 매수 |
| SELL | 매도 |

---

## CONTRACT

> 프리랜서 계약 정보를 저장합니다.

| 컬럼명                | 데이터 타입   | 설명        | Null 허용 | PK / FK |
| --------------------- | ------------- | ----------- | --------- | ------- |
| contract_id           | BIGINT        | 계약 ID     | NO        | PK      |
| user_id               | BIGINT        | 사용자 ID   | NO        | FK      |
| client_name           | VARCHAR(255)  | 거래처명    | NO        | -       |
| contract_amount       | DECIMAL(18,2) | 계약 금액   | NO        | -       |
| tax_type              | ENUM          | 세금 유형   | NO        | -       |
| tax_rate              | DECIMAL(5,2)  | 세율        | NO        | -       |
| expected_payment_date | DATE          | 예상 입금일 | YES       | -       |
| actual_payment_date   | DATE          | 실제 입금일 | YES       | -       |
| contract_status       | ENUM          | 계약 상태   | NO        | -       |
| memo                  | TEXT          | 메모        | YES       | -       |
| created_at            | TIMESTAMP     | 생성일      | NO        | -       |

---

## CONTRACT_SETTLEMENT

> 계약 정산 정보를 저장합니다.

| 컬럼명          | 데이터 타입   | 설명      | Null 허용 | PK / FK |
| --------------- | ------------- | --------- | --------- | ------- |
| settlement_id   | BIGINT        | 정산 ID   | NO        | PK      |
| contract_id     | BIGINT        | 계약 ID   | NO        | FK      |
| tax_rate        | DECIMAL(5,2)  | 세율      | NO        | -       |
| deducted_amount | DECIMAL(18,2) | 공제 금액 | NO        | -       |
| actual_income   | DECIMAL(18,2) | 실수령액  | NO        | -       |
| calculated_at   | TIMESTAMP     | 계산 시각 | NO        | -       |

---

## PAYMENT_MATCHING

> 계약 입금 매칭 정보를 저장합니다.

| 컬럼명              | 데이터 타입 | 설명         | Null 허용 | PK / FK |
| ------------------- | ----------- | ------------ | --------- | ------- |
| matching_id         | BIGINT      | 매칭 ID      | NO        | PK      |
| contract_id         | BIGINT      | 계약 ID      | NO        | FK      |
| bank_transaction_id | BIGINT      | 은행 거래 ID | NO        | -       |
| matching_status     | ENUM        | 매칭 상태    | NO        | -       |
| matched_by          | ENUM        | 매칭 주체    | NO        | -       |
| matched_at          | TIMESTAMP   | 매칭 시각    | YES       | -       |

---

## VIRTUAL_SALARY_SETTING

> 가상 월급 설정 정보를 저장합니다.

| 컬럼명                  | 데이터 타입   | 설명                  | Null 허용 | PK / FK |
| ----------------------- | ------------- | --------------------- | --------- | ------- |
| user_id                 | BIGINT        | 사용자 ID             | NO        | PK, FK  |
| target_salary           | DECIMAL(18,2) | 목표 월급             | NO        | -       |
| payday                  | INT           | 월급일                | NO        | -       |
| emergency_target_amount | DECIMAL(18,2) | 비상금 목표 금액      | YES       | -       |
| investment_amount       | DECIMAL(18,2) | 투자 이체 고정 금액   | YES       | -       |
| emergency_amount        | DECIMAL(18,2) | 비상금 이체 고정 금액 | YES       | -       |
| priority_order          | JSON          | 우선순위 설정         | YES       | -       |
| updated_at              | TIMESTAMP     | 수정일                | NO        | -       |

---

## FAVORITE_STOCK

> 관심 종목 정보를 저장합니다.

| 컬럼명            | 데이터 타입 | 설명         | Null 허용 | PK / FK |
| ----------------- | ----------- | ------------ | --------- | ------- |
| favorite_stock_id | BIGINT      | 관심 종목 ID | NO        | PK      |
| user_id           | BIGINT      | 사용자 ID    | NO        | FK      |
| stock_code        | VARCHAR(20) | 종목 코드    | NO        | -       |
| created_at        | TIMESTAMP   | 생성일       | NO        | -       |

---

## AI_CHAT_SESSION

> AI 채팅 세션 정보를 저장합니다.

| 컬럼명       | 데이터 타입  | 설명                                     | Null 허용 | PK / FK |
| ------------ | ------------ | ---------------------------------------- | --------- | ------- |
| session_id   | BIGINT       | 세션 ID                                  | NO        | PK      |
| user_id      | BIGINT       | 사용자 ID                                | NO        | FK      |
| title        | VARCHAR(255) | 세션 제목                                | YES       | -       |
| session_type | VARCHAR(20)  | 세션 유형 (CHAT/TRANSFER/STOCK/ANALYSIS) | NO        | -       |
| status       | VARCHAR(20)  | 세션 상태 (ACTIVE/CLOSED)                | NO        | -       |
| created_at   | TIMESTAMP    | 생성일                                   | NO        | -       |
| updated_at   | TIMESTAMP    | 수정일                                   | NO        | -       |

---

## AI_CHAT_MESSAGE

> AI 채팅 메시지를 저장합니다.

| 컬럼명              | 데이터 타입 | 설명                    | Null 허용 | PK / FK |
| ------------------- | ----------- | ----------------------- | --------- | ------- |
| message_id          | BIGINT      | 메시지 ID               | NO        | PK      |
| session_id          | BIGINT      | 세션 ID                 | NO        | FK      |
| role                | VARCHAR(10) | 메시지 역할 (USER/AI)   | NO        | -       |
| content             | TEXT        | 메시지 내용             | NO        | -       |
| intent              | VARCHAR(50) | AI 응답 의도 (ASSET 등) | YES       | -       |
| action_type         | VARCHAR(50) | 액션 유형               | YES       | -       |
| action_confirmed_yn | BOOLEAN     | 액션 승인 여부          | NO        | -       |
| created_at          | TIMESTAMP   | 생성일                  | NO        | -       |

---

## NOTIFICATION

> 사용자 알림 데이터를 저장합니다.

| 컬럼명          | 데이터 타입 | 설명      | Null 허용 | PK / FK |
| --------------- | ----------- | --------- | --------- | ------- |
| notification_id | BIGINT      | 알림 ID   | NO        | PK      |
| user_id         | BIGINT      | 사용자 ID | NO        | FK      |
| type            | VARCHAR(50) | 알림 유형 | NO        | -       |
| content         | TEXT        | 알림 내용 | NO        | -       |
| read_yn         | BOOLEAN     | 읽음 여부 | NO        | -       |
| created_at      | TIMESTAMP   | 생성일    | NO        | -       |

---

## AI_BRIEFING

> AI 브리핑 데이터를 저장합니다.

| 컬럼명        | 데이터 타입 | 설명        | Null 허용 | PK / FK |
| ------------- | ----------- | ----------- | --------- | ------- |
| briefing_id   | BIGINT      | 브리핑 ID   | NO        | PK      |
| user_id       | BIGINT      | 사용자 ID   | NO        | FK      |
| briefing_type | ENUM        | 브리핑 유형 | NO        | -       |
| content       | TEXT        | 브리핑 내용 | NO        | -       |
| created_at    | TIMESTAMP   | 생성일      | NO        | -       |

---

# 설계 특징

- 사용자 중심 통합 금융 데이터 구조
- 마이데이터 기반 통합 거래내역 관리
- 계약 기반 프리랜서 수입 관리
- AI 채팅 및 액션 추적 지원
- 금융 데이터 감사(Audit) 가능 구조
- 가상 월급 및 자동 분배 기능 지원
