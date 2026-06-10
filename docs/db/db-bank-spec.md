# db-bank-spec.md

# 은행 DB 명세

## 개요

은행 DB는 계좌 및 거래 원장 데이터를 저장하는 핵심 금융 데이터베이스입니다.

금융 원장의 정확성과 불변성 보장을 최우선으로 하며, 외부 네트워크와 분리된 온프레미스 폐쇄망에서 운영합니다.

| 항목 | 내용            |
|----|---------------|
| 위치 | 온프레미스 (폐쇄망)   |
| DB | OracleDB      |
| 역할 | 계좌 및 거래 원장 관리 |

---

## 테이블 목록

| 테이블명                  | 역할              |
|-----------------------|-----------------|
| BANK_ACCOUNT          | 계좌 기본 정보        |
| BANK_TRANSACTION      | 계좌 거래 내역 원장     |
| TRANSFER_TRANSACTION  | 이체 내역           |
| ACCOUNT_BALANCE_HISTORY | 일별 잔액 스냅샷 (미구현) |

---

## 테이블 명세

### BANK_ACCOUNT

#### 역할

사용자의 은행 계좌 기본 정보를 관리합니다.

계좌 원장의 최상위 엔티티로, 계좌번호, 잔액, 현재 상태를 저장합니다.

#### DDL

```sql
CREATE SEQUENCE SEQ_BANK_ACCOUNT START WITH 1 INCREMENT BY 1;

CREATE TABLE BANK_ACCOUNT
(
    ACCOUNT_ID     NUMBER(19)     DEFAULT SEQ_BANK_ACCOUNT.NEXTVAL PRIMARY KEY,
    USER_ID        NUMBER(19)     NOT NULL,
    BANK_CODE      VARCHAR2(20)   NOT NULL,
    ACCOUNT_NUMBER VARCHAR2(50)   NOT NULL UNIQUE,
    ACCOUNT_NAME   VARCHAR2(100)  NOT NULL,
    BALANCE        NUMBER(18, 2)  NOT NULL,
    ACCOUNT_STATUS VARCHAR2(20)   NOT NULL,
    OPENED_AT      TIMESTAMP      NOT NULL,
    CLOSED_AT      TIMESTAMP,
    UPDATED_AT     TIMESTAMP
);
```

#### 컬럼 설명

| 컬럼             | 타입            | 설명            | Null 허용 |
|----------------|---------------|---------------|---------|
| ACCOUNT_ID     | NUMBER(19)    | PK            | NO      |
| USER_ID        | NUMBER(19)    | 계좌 소유 사용자 ID  | NO      |
| BANK_CODE      | VARCHAR2(20)  | 은행 코드         | NO      |
| ACCOUNT_NUMBER | VARCHAR2(50)  | 계좌번호 (유일)     | NO      |
| ACCOUNT_NAME   | VARCHAR2(100) | 계좌명           | NO      |
| BALANCE        | NUMBER(18,2)  | 현재 잔액         | NO      |
| ACCOUNT_STATUS | VARCHAR2(20)  | 계좌 상태         | NO      |
| OPENED_AT      | TIMESTAMP     | 개설일           | NO      |
| CLOSED_AT      | TIMESTAMP     | 해지일 (해지 시 기록) | YES     |
| UPDATED_AT     | TIMESTAMP     | 최근 잔액 변경 시각   | YES     |

#### ACCOUNT_STATUS 값

| 값       | 설명    |
|---------|-------|
| ACTIVE  | 정상    |
| DORMANT | 휴면    |
| LOCKED  | 잠금    |
| CLOSED  | 해지    |

#### 인덱스

| 이름                              | 컬럼             | 설명          |
|---------------------------------|----------------|-------------|
| UK_BANK_ACCOUNT_NUMBER          | ACCOUNT_NUMBER | 계좌번호 유일성 보장 |
| IDX_BANK_ACCOUNT_USER_ID        | USER_ID        | 사용자별 계좌 조회  |
| IDX_BANK_ACCOUNT_STATUS         | ACCOUNT_STATUS | 상태별 조회      |

---

### BANK_TRANSACTION

#### 역할

계좌의 모든 거래를 원장으로 저장합니다.

거래 원장은 절대 삭제하거나 수정하지 않습니다.

#### DDL

```sql
CREATE SEQUENCE SEQ_BANK_TRANSACTION START WITH 1 INCREMENT BY 1;

CREATE TABLE BANK_TRANSACTION
(
    TRANSACTION_ID          NUMBER(19)    DEFAULT SEQ_BANK_TRANSACTION.NEXTVAL PRIMARY KEY,
    ACCOUNT_ID              NUMBER(19)    NOT NULL,
    TRANSACTION_TYPE        VARCHAR2(30)  NOT NULL,
    AMOUNT                  NUMBER(18, 2) NOT NULL,
    BALANCE_AFTER           NUMBER(18, 2) NOT NULL,
    OPPOSITE_BANK_CODE      VARCHAR2(20),
    OPPOSITE_ACCOUNT_NUMBER VARCHAR2(50),
    TRANSACTION_CHANNEL     VARCHAR2(20)  NOT NULL,
    TRANSACTION_STATUS      VARCHAR2(20)  NOT NULL,
    TRANSACTION_AT          TIMESTAMP     NOT NULL,
    CONSTRAINT FK_BANK_TX_ACCOUNT FOREIGN KEY (ACCOUNT_ID) REFERENCES BANK_ACCOUNT (ACCOUNT_ID),
    CONSTRAINT CHK_BANK_TX_AMOUNT CHECK (AMOUNT > 0)
);
```

#### 컬럼 설명

| 컬럼                      | 타입            | 설명                          | Null 허용 |
|-------------------------|---------------|-----------------------------|---------|
| TRANSACTION_ID          | NUMBER(19)    | PK                          | NO      |
| ACCOUNT_ID              | NUMBER(19)    | 대상 계좌 ID (BANK_ACCOUNT FK)  | NO      |
| TRANSACTION_TYPE        | VARCHAR2(30)  | 거래 유형                       | NO      |
| AMOUNT                  | NUMBER(18,2)  | 거래 금액 (항상 양수)               | NO      |
| BALANCE_AFTER           | NUMBER(18,2)  | 거래 후 잔액 스냅샷                 | NO      |
| OPPOSITE_BANK_CODE      | VARCHAR2(20)  | 상대 은행 코드 (이체 시)             | YES     |
| OPPOSITE_ACCOUNT_NUMBER | VARCHAR2(50)  | 상대 계좌번호 (이체 시)              | YES     |
| TRANSACTION_CHANNEL     | VARCHAR2(20)  | 거래 채널                       | NO      |
| TRANSACTION_STATUS      | VARCHAR2(20)  | 거래 상태                       | NO      |
| TRANSACTION_AT          | TIMESTAMP     | 거래 발생 시각                    | NO      |

#### TRANSACTION_TYPE 값

| 값             | 설명        | 입출금 |
|---------------|-----------|-----|
| DEPOSIT       | 입금        | 입금  |
| WITHDRAW      | 출금        | 출금  |
| TRANSFER_IN   | 이체 입금     | 입금  |
| TRANSFER_OUT  | 이체 출금     | 출금  |
| AUTO_TRANSFER | 자동이체 출금   | 출금  |

#### TRANSACTION_CHANNEL 값

| 값        | 설명      |
|----------|---------|
| APP      | 앱 직접 요청 |
| AI_AGENT | AI 자동 요청 |

#### TRANSACTION_STATUS 값

| 값         | 설명  |
|-----------|-----|
| SUCCESS   | 성공  |
| FAILED    | 실패  |
| CANCELLED | 취소  |

#### 인덱스

| 이름                        | 컬럼                          | 설명              |
|---------------------------|-------------------------------|-----------------|
| IDX_BANK_TX_ACCOUNT_AT    | ACCOUNT_ID, TRANSACTION_AT    | 계좌별 거래 시각순 조회   |

#### 제약

```sql
-- ACCOUNT_ID FK
ALTER TABLE BANK_TRANSACTION
    ADD CONSTRAINT FK_BANK_TX_ACCOUNT
        FOREIGN KEY (ACCOUNT_ID) REFERENCES BANK_ACCOUNT (ACCOUNT_ID);

-- 금액은 항상 양수
ALTER TABLE BANK_TRANSACTION
    ADD CONSTRAINT CHK_BANK_TX_AMOUNT
        CHECK (AMOUNT > 0);
```

---

### TRANSFER_TRANSACTION

#### 역할

계좌 간 이체 정보를 저장합니다.

이체 승인 시 출금 계좌(TRANSFER_OUT)와 입금 계좌(TRANSFER_IN) 각 1건씩 BANK_TRANSACTION을 생성하며,
`FROM_ACCOUNT_TRANSACTION_ID` / `TO_ACCOUNT_TRANSACTION_ID`로 두 원장을 연결합니다.

입금 대상이 타 은행인 경우 `TO_ACCOUNT_ID`는 NULL이며, `TO_BANK_CODE` / `TO_ACCOUNT_NUMBER`로 식별합니다.

#### DDL

```sql
CREATE SEQUENCE SEQ_TRANSFER_TRANSACTION START WITH 1 INCREMENT BY 1;

CREATE TABLE TRANSFER_TRANSACTION
(
    TRANSFER_ID                  NUMBER(19)    DEFAULT SEQ_TRANSFER_TRANSACTION.NEXTVAL PRIMARY KEY,
    FROM_ACCOUNT_ID              NUMBER(19)    NOT NULL,
    TO_ACCOUNT_ID                NUMBER(19),
    TO_BANK_CODE                 VARCHAR2(20)  NOT NULL,
    TO_ACCOUNT_NUMBER            VARCHAR2(50)  NOT NULL,
    TRANSFER_AMOUNT              NUMBER(18, 2) NOT NULL,
    REQUESTED_BY                 VARCHAR2(20)  NOT NULL,
    TRANSFER_STATUS              VARCHAR2(20)  NOT NULL,
    FAILURE_REASON               VARCHAR2(500),
    REQUESTED_AT                 TIMESTAMP     NOT NULL,
    COMPLETED_AT                 TIMESTAMP,
    FROM_ACCOUNT_TRANSACTION_ID  NUMBER(19),
    TO_ACCOUNT_TRANSACTION_ID    NUMBER(19),
    CONSTRAINT FK_TRANSFER_FROM_ACCOUNT FOREIGN KEY (FROM_ACCOUNT_ID) REFERENCES BANK_ACCOUNT (ACCOUNT_ID),
    CONSTRAINT FK_TRANSFER_TO_ACCOUNT   FOREIGN KEY (TO_ACCOUNT_ID)   REFERENCES BANK_ACCOUNT (ACCOUNT_ID),
    CONSTRAINT CHK_TRANSFER_AMOUNT CHECK (TRANSFER_AMOUNT > 0)
);
```

#### 컬럼 설명

| 컬럼                          | 타입            | 설명                               | Null 허용 |
|-----------------------------|---------------|----------------------------------|---------|
| TRANSFER_ID                 | NUMBER(19)    | PK                               | NO      |
| FROM_ACCOUNT_ID             | NUMBER(19)    | 출금 계좌 ID (BANK_ACCOUNT FK)      | NO      |
| TO_ACCOUNT_ID               | NUMBER(19)    | 입금 계좌 ID (동행 이체 시, 타행이면 NULL)   | YES     |
| TO_BANK_CODE                | VARCHAR2(20)  | 입금 은행 코드                        | NO      |
| TO_ACCOUNT_NUMBER           | VARCHAR2(50)  | 입금 계좌번호                         | NO      |
| TRANSFER_AMOUNT             | NUMBER(18,2)  | 이체 금액 (항상 양수)                   | NO      |
| REQUESTED_BY                | VARCHAR2(20)  | 이체 요청 주체                        | NO      |
| TRANSFER_STATUS             | VARCHAR2(20)  | 이체 처리 상태                        | NO      |
| FAILURE_REASON              | VARCHAR2(500) | 실패 사유 (실패 시에만 기록)               | YES     |
| REQUESTED_AT                | TIMESTAMP     | 이체 요청 시각                        | NO      |
| COMPLETED_AT                | TIMESTAMP     | 이체 완료 시각 (성공/취소 시 기록)           | YES     |
| FROM_ACCOUNT_TRANSACTION_ID | NUMBER(19)    | 출금 원장 레코드 ID (approve 후 연결)     | YES     |
| TO_ACCOUNT_TRANSACTION_ID   | NUMBER(19)    | 입금 원장 레코드 ID (approve 후 연결)     | YES     |

#### TRANSFER_STATUS 값

| 값          | 설명                        |
|------------|---------------------------|
| REQUESTED  | 이체 요청 생성 (잔액 미차감)         |
| PROCESSING | Saga 처리 중                 |
| SUCCESS    | 이체 완료 (잔액 차감/입금 완료)       |
| FAILED     | 이체 실패                     |
| CANCELLED  | Saga 보상 트랜잭션으로 취소         |

#### REQUESTED_BY 값

| 값    | 설명       |
|------|----------|
| USER | 사용자 직접 요청 |
| AI   | AI 자동 요청 |

#### 인덱스

| 이름                                  | 컬럼                | 설명           |
|-------------------------------------|---------------------|--------------|
| IDX_TRANSFER_FROM_ACCOUNT_ID        | FROM_ACCOUNT_ID     | 출금 계좌별 이체 조회 |
| IDX_TRANSFER_TO_ACCOUNT_ID          | TO_ACCOUNT_ID       | 입금 계좌별 이체 조회 |
| IDX_TRANSFER_STATUS                 | TRANSFER_STATUS     | 상태별 조회       |
| IDX_TRANSFER_REQUESTED_AT           | REQUESTED_AT        | 요청 시각순 조회    |

#### 제약

```sql
-- FROM_ACCOUNT FK
ALTER TABLE TRANSFER_TRANSACTION
    ADD CONSTRAINT FK_TRANSFER_FROM_ACCOUNT
        FOREIGN KEY (FROM_ACCOUNT_ID) REFERENCES BANK_ACCOUNT (ACCOUNT_ID);

-- TO_ACCOUNT FK (nullable — 타행 이체 시 NULL 허용)
ALTER TABLE TRANSFER_TRANSACTION
    ADD CONSTRAINT FK_TRANSFER_TO_ACCOUNT
        FOREIGN KEY (TO_ACCOUNT_ID) REFERENCES BANK_ACCOUNT (ACCOUNT_ID);

-- 금액은 항상 양수
ALTER TABLE TRANSFER_TRANSACTION
    ADD CONSTRAINT CHK_TRANSFER_AMOUNT
        CHECK (TRANSFER_AMOUNT > 0);
```

---

### ACCOUNT_BALANCE_HISTORY

#### 역할

계좌의 일별 종가 잔액을 스냅샷으로 저장합니다.

정산, 대사, 통계 용도로 활용합니다.

> **현재 미구현 상태입니다.** 엔티티 클래스(AccountBalanceHistory.java)는 생성되어 있으나 컬럼 정의가 없습니다.

---

## 잔액 정합성 규칙

### 이체 원장 기록 원칙

이체 승인(approve) 시 TRANSFER_OUT / TRANSFER_IN 각 1건씩 총 2건의 BANK_TRANSACTION을 생성합니다.

```
이체 발생 시 원장 기록 예시:

[출금 계좌] BANK_TRANSACTION
  TRANSACTION_TYPE = TRANSFER_OUT
  AMOUNT           = 100,000
  BALANCE_AFTER    = (이전 잔액 - 100,000)

[입금 계좌] BANK_TRANSACTION
  TRANSACTION_TYPE = TRANSFER_IN
  AMOUNT           = 100,000
  BALANCE_AFTER    = (이전 잔액 + 100,000)
```

### 잔액 검증

- `BALANCE_AFTER`는 직전 거래의 `BALANCE_AFTER`를 기준으로 계산
- `BANK_ACCOUNT.BALANCE`는 입출금 시 실시간 갱신 (`UPDATED_AT` 함께 기록)
- 불일치 시 `RECONCILIATION_RESULT`에 기록

---

## 운영 규칙

| 항목     | 규칙                                                    |
|--------|-------------------------------------------------------|
| 데이터 변경 | BANK_TRANSACTION INSERT only, UPDATE/DELETE 금지        |
| 금액 타입  | NUMBER(18,2) 사용, float/double 금지                      |
| 계좌 해지  | CLOSED_AT 기록, 레코드 삭제 금지                               |
| 잔액 계산  | BANK_ACCOUNT.BALANCE 컬럼 사용, 실시간 합산 금지               |
| 이체 취소  | TRANSFER_STATUS → CANCELLED 전이, 실제 잔액 변동 없음          |
| 네트워크   | 온프레미스 폐쇄망 내부에서만 접근 허용                               |
