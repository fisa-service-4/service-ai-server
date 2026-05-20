# 기술 스택

## tech-stack.md

 
---

## Backend

| 기술                   | 설명               | 버전  |
|----------------------|------------------|-----|
| Java                 | 백엔드 언어           | 17  |
| Spring Boot          | 백엔드 애플리케이션 서버    | 3.x |
| Spring Data JPA      | ORM 데이터 접근       |
| Spring Security      | 인증 및 인가          |
| Spring Cloud Gateway | 온프레미스 내부 Gateway |

 
---

## AI

| 기술        | 설명              | 버전   |
|-----------|-----------------|------|
| Python    | AI 서비스 언어       | 3.11 |
| FastAPI   | AI 서비스 API 서버   |
| LangGraph | Agent 구성        |
| Qwen3-8B  | 로컬 LLM (Ollama) |
| BGE-M3    | 임베딩 모델          |
| pgvector  | Vector DB       |

 
---

## Frontend

| 기술         | 설명               | 버전 |
|------------|------------------|----|
| Next.js    | React 기반 프레임워크   |
| TypeScript | 정적 타입 JavaScript |

 
---

## Database

| 기술         | 설명              | 버전  |
|------------|-----------------|-----|
| PostgreSQL | 운영 DB (RDS)     | 16  |
| PostgreSQL | 분석 DB (EC2)     | 16  |
| PostgreSQL | 로그 DB (EC2)     | 16  |
| pgvector   | Vector DB (EC2) |
| Redis      | 세션/캐시 (EC2)     | 7.2 |

 
---

## Message Queue

| 기술    | 설명                  | 버전  
|-------|---------------------|-----|
| Kafka | 온프레미스, 거래 이벤트 저장/감사 | 3.8 |

 
---

## Infrastructure

| 기술               | 설명                                 |
|------------------|------------------------------------|
| AWS              | ALB, Nginx, Bastion Host, RDS, EC2 |
| Docker           | 컨테이너 기반 환경 구성                      |
| Jenkins          | CI/CD 파이프라인 자동화                    |
| SonarQube        | 코드 품질 및 정적 분석                      |
| Site-to-Site VPN | pfSense + strongSwan               |