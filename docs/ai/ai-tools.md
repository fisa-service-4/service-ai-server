# AI Tools

## Tool 목록
| 분류 | Tool | 설명 |
| --- | --- | --- |
| 분석 | get_analysis_data | 분석 DB 데이터 조회 |
| 자산 | get_total_asset | 총 자산 조회 |
| 자산 | get_bank_balance | 은행 잔액 조회 |
| 계약 | get_contracts | 계약 목록 조회 |
| 계약 | get_pending_income | 미입금 조회 |
| 가상월급 | get_virtual_salary_setting | 가상월급 설정 조회 |
| 가상월급 | update_salary_setting | 가상월급 설정 변경 |
| 증권 | search_stock | 종목 검색 |
| 증권 | get_stock_price | 현재가 조회 |
| 증권 | get_securities_balance | 예수금 조회 |
| 증권 | execute_buy_order | 매수 주문 |
| 증권 | execute_sell_order | 매도 주문 |
| 인증 | check_pin_status | PIN 상태 확인 |
| 인증 | verify_pin | PIN 인증 |
| 이체 | get_bank_accounts | 계좌 목록 조회 |
| 이체 | get_transfer_limit | 이체 한도 조회 |
| 이체 | execute_transfer | 이체 실행 |
| 이체 | get_transfer_history | 이체 내역 조회 |

---

## Tool 호출 방식
```
AI Agent → Tool 호출
→ 백엔드 API 호출 (DB 직접 접근 금지)
→ 백엔드가 데이터 조회 후 반환
→ Agent가 결과 활용
```