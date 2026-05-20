# bank-server API 명세

> Port: `8081`

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