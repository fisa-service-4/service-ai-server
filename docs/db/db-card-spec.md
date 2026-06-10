# db-card-spec.md

# Card DB 명세서

카드 DB는 카드 정보 및 카드 승인(결제) 데이터를 관리합니다.

금융 감사 및 소비 분석을 위해 승인 이력을 별도로 저장하며,
승인 상태 및 실패 사유를 관리합니다.

---

## 테이블 목록

| 테이블명          | 설명          |
|---------------|-------------|
| CARD_MASTER   | 카드 기본 정보    |
| CARD_APPROVAL | 카드 승인/결제 이력 |

---

## CARD_MASTER

> 사용자 카드 정보를 저장합니다.

| 컬럼명               | 데이터 타입       | 설명       | Null 허용 | PK / FK |
|-------------------|--------------|----------|---------|---------|
| card_id           | BIGINT       | 카드 ID    | NO      | PK      |
| user_id           | BIGINT       | 사용자 ID   | NO      | -       |
| linked_account_id | BIGINT       | 연결 계좌 ID | YES     | -       |
| card_number       | VARCHAR(100) | 카드 번호    | NO      | UNIQUE  |
| card_status       | VARCHAR(20)  | 카드 상태    | NO      | -       |

### card_status 값

현재 서비스 정책상 카드 상태는 ACTIVE만 사용합니다.

| 값         | 설명 |
|-----------|----|
| ACTIVE    | 정상 |
| LOST      | 분실 |
| EXPIRED   | 만료 |
| SUSPENDED | 정지 |
| CLOSED    | 해지 |

---

## CARD_APPROVAL

> 카드 승인 및 결제 이력을 저장합니다.

| 컬럼명                    | 데이터 타입        | 설명                        | Null 허용 | PK / FK |
|------------------------|---------------|---------------------------|---------|---------|
| approval_id            | BIGINT        | 승인 이력 ID                  | NO      | PK      |
| card_id                | BIGINT        | 카드 ID                     | NO      | FK      |
| account_transaction_id | BIGINT        | 연결된 은행 거래 ID (account_transaction FK) | YES     | -       |
| merchant_name          | VARCHAR(255)  | 가맹점명                      | NO      | -       |
| merchant_category      | VARCHAR(50)   | 가맹점 카테고리 (TransactionCategory 참고) | YES     | -       |
| approval_amount        | DECIMAL(18,2) | 승인 금액                     | NO      | -       |
| approval_status        | VARCHAR(20)   | 승인 상태                     | NO      | -       |
| approval_code          | VARCHAR(100)  | 승인 코드                     | YES     | -       |
| declined_reason        | VARCHAR(255)  | 승인 거절 사유                  | YES     | -       |
| approved_at            | TIMESTAMP     | 승인 시각                     | NO      | -       |

### approval_status 값

| 값         | 설명    |
|-----------|-------|
| APPROVED  | 승인    |
| DECLINED  | 거절    |
| CANCELLED | 승인 취소 |

### merchant_category 값 (MerchantCategory)

> 카드 결제 전용 enum. 은행 원장 분류와 별개로 관리.
> DB는 VARCHAR(50) 저장, 애플리케이션 레이어에서 Java enum으로 유효성 검사.

| 값              | 설명       |
|----------------|----------|
| FOOD_BEVERAGE  | 식음료      |
| CAFE           | 카페       |
| TRANSPORTATION | 교통       |
| SHOPPING       | 쇼핑       |
| MART           | 마트 / 편의점 |
| ENTERTAINMENT  | 여가 / 문화  |
| MEDICAL        | 의료 / 건강  |
| EDUCATION      | 교육       |
| SUBSCRIPTION   | 구독       |
| COMMUNICATION  | 통신       |
| BEAUTY         | 뷰티 / 미용  |
| TRAVEL         | 여행       |
| GAS            | 주유       |
| ETC            | 기타       |

---

# 주요 관계

| 부모 테이블         | 자식 테이블        | 설명                           |
|----------------|---------------|------------------------------|
| CARD_MASTER    | CARD_APPROVAL | 카드별 승인 이력                    |
| account_transaction (Bank DB) | CARD_APPROVAL | 카드 승인 ↔ 은행 원장 매핑 (nullable) |

> `account_transaction_id`는 nullable FK로, 현재 Mock 데이터 단계에서는 연결 없이 운영 가능하다.
> 실제 카드 승인 → 계좌 출금 연계 시 해당 컬럼을 통해 추적한다.

---

# 설계 특징

- 카드 승인 이력 별도 저장
- 승인 실패 사유 관리
- 소비 분석을 위한 가맹점 카테고리 저장
- 카드 상태 기반 사용 제한 관리
- 금융 감사(Audit) 추적 가능 구조
- `account_transaction_id`를 통한 카드 승인 ↔ 은행 원장 연결 지원 (nullable)