# API Index

## 공통

| 파일                   | 언제 참조                              |
| ---------------------- | -------------------------------------- |
| @api/api-convention.md | API 작성 규칙/공통 응답 형식 확인할 때 |
| @api/error-code.md     | 에러 코드 확인할 때                    |

## 서버별 API

| 파일                       | 설명                      | 언제 참조                        |
| -------------------------- | ------------------------- | -------------------------------- |
| @api-service-backend.md    | 핵심 서비스 API 명세      | 회원/계약/알림/가상월급 개발 시  |
| @api-bank-server.md        | 은행 원장 API 명세        | 계좌/이체/거래내역 기능 개발 시  |
| @api-stock-server.md       | 증권 원장 API 명세        | 주문/체결/보유종목 기능 개발 시  |
| @api-transaction-server.md | Saga/이벤트 처리 API 명세 | 분산 트랜잭션 및 DLQ 작업 시     |
| @api-mydata-server.md      | 마이데이터 API 명세       | 금융기관 연동 및 동기화 작업 시  |
| @api-ai-server.md          | AI 분석 API 명세          | AI 채팅/분석/브리핑 기능 개발 시 |
