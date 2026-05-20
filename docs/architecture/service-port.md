# service-port.md

# Service Port

프로젝트 서비스 및 인프라 포트 목록입니다.

로컬 개발 및 Docker 환경 기준 포트입니다.

---

## Application

| 서비스                | 포트   |
|--------------------|------|
| service-frontend   | 5173 |
| service-backend    | 8080 |
| service-ai-server  | 8000 |
| bank-server        | 8081 |
| stock-server       | 8082 |
| transaction-server | 8083 |
| mydata-server      | 8084 |

---

## Infrastructure

| 서비스        | 포트    |
|------------|-------|
| PostgreSQL | 5432  |
| Redis      | 6379  |
| Kafka      | 9092  |
| Kafka UI   | 8085  |
| Ollama     | 11434 |

---

## 규칙

- 내부 포트 기준으로 관리합니다.
- 로컬 개발 환경 기준입니다.
- 운영 환경(AWS)은 Reverse Proxy 및 Gateway를 통해 라우팅합니다.
- 동일 EC2 내부에서는 포트 중복이 발생하지 않아야 합니다.