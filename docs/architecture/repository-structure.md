# repository-structure.md

# Repository Structure

## 멀티 레포 구조

| Repository         | 역할                              |
|--------------------|---------------------------------|
| service-frontend   | Next.js Frontend 및 BFF          |
| service-backend    | 핵심 비즈니스 서버                      |
| service-ai-server  | AI Agent 서버                     |
| bank-server        | 은행 Mock 서버                      |
| stock-server       | 증권 Mock 서버                      |
| transaction-server | 거래/Saga 서버                      |
| mydata-server      | 마이데이터 Mock 서버                   |
| infra              | Docker, Nginx, Jenkins 등 인프라 관리 |

---

# 서비스 역할

## service-frontend

- 사용자 화면
- API 연동
- 인증 상태 관리

---

## service-backend

- 인증/인가
- 사용자 관리
- 자산 요약
- 가상 월급
- 알림

---

## service-ai-server

- 금융 분석
- 소비 패턴 분석
- 투자 성향 분석
- 챗봇

---

## bank-server

- 계좌 조회
- 계좌 이체
- 거래내역 조회

---

## stock-server

- 주식 주문
- 보유 주식 조회
- 관심 종목 관리

---

## transaction-server

- 거래 원장 관리
- Saga 상태 관리
- 이벤트 저장
- 감사 로그 관리

---

## mydata-server

- 마이데이터 연동 Mock
- 외부 자산 조회