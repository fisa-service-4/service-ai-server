# system-architecture.md

# System Architecture

# 아키텍처 구성

- AWS 서비스망
- 온프레미스 계정계망
- Site-to-Site VPN 기반 하이브리드 구조

---

# 주요 서버 구성

| 서버                 | 역할            | 위치    |
|--------------------|---------------|-------|
| service-frontend   | 사용자 UI 및 BFF  | AWS   |
| service-backend    | 핵심 비즈니스 로직    | AWS   |
| service-ai-server  | AI Agent 및 분석 | AWS   |
| bank-server        | 은행 Mock 서버    | 온프레미스 |
| stock-server       | 증권 Mock 서버    | 온프레미스 |
| transaction-server | 거래 원장 및 Saga  | 온프레미스 |
| mydata-server      | 마이데이터 Mock 서버 | AWS   |

---

# 데이터 흐름

1. 사용자가 Frontend 요청
2. service-backend 비즈니스 처리
3. 금융 데이터 필요 시 VPN 통해 온프레미스 접근
4. transaction-server 이벤트 저장
5. Kafka 기반 이벤트 처리
6. AI 서버 분석 결과 반환

---

# 주요 아키텍처 패턴

- MSA(Microservice Architecture)
- Saga Pattern
- Transactional Outbox Pattern
- Event Driven Architecture
- Hybrid Cloud Architecture