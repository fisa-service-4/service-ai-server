# stock-server API 명세

> Port: `8082`

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