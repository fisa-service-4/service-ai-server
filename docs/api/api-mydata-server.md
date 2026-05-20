# mydata-server API 명세

> Port: `8084`

---

## BANK API

| Method | URL                                | 설명          | 인증     |
|--------|------------------------------------|-------------|--------|
| GET    | /mydata/bank/accounts              | 은행 계좌 목록 조회 | Bearer |
| GET    | /mydata/bank/accounts/{accountId}  | 은행 계좌 상세 조회 | Bearer |
| POST   | /mydata/bank/accounts/transactions | 은행 거래내역 조회  | Bearer |

---

## INVEST API

| Method | URL                                  | 설명          | 인증     |
|--------|--------------------------------------|-------------|--------|
| GET    | /mydata/invest/accounts              | 증권 계좌 목록 조회 | Bearer |
| POST   | /mydata/invest/accounts/transactions | 증권 거래내역 조회  | Bearer |
| POST   | /mydata/invest/accounts/products     | 보유종목 조회     | Bearer |