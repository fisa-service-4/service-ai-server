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
| card_status       | ENUM         | 카드 상태    | NO      | -       |

### card_status (ENUM)

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

| 컬럼명               | 데이터 타입        | 설명       | Null 허용 | PK / FK |
|-------------------|---------------|----------|---------|---------|
| approval_id       | BIGINT        | 승인 이력 ID | NO      | PK      |
| card_id           | BIGINT        | 카드 ID    | NO      | FK      |
| merchant_name     | VARCHAR(255)  | 가맹점명     | NO      | -       |
| merchant_category | VARCHAR(100)  | 가맹점 카테고리 | YES     | -       |
| approval_amount   | DECIMAL(18,2) | 승인 금액    | NO      | -       |
| approval_status   | ENUM          | 승인 상태    | NO      | -       |
| approval_code     | VARCHAR(100)  | 승인 코드    | YES     | -       |
| declined_reason   | VARCHAR(255)  | 승인 거절 사유 | YES     | -       |
| approved_at       | TIMESTAMP     | 승인 시각    | NO      | -       |

### approval_status (ENUM)

| 값         | 설명    |
|-----------|-------|
| APPROVED  | 승인    |
| DECLINED  | 거절    |
| CANCELLED | 승인 취소 |

---

# 주요 관계

| 부모 테이블      | 자식 테이블        | 설명        |
|-------------|---------------|-----------|
| CARD_MASTER | CARD_APPROVAL | 카드별 승인 이력 |

---

# 설계 특징

- 카드 승인 이력 별도 저장
- 승인 실패 사유 관리
- 소비 분석을 위한 가맹점 카테고리 저장
- 카드 상태 기반 사용 제한 관리
- 금융 감사(Audit) 추적 가능 구조