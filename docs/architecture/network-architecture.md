# network-architecture.md

# Network Architecture

# 전체 구조

- AWS 서비스망
- 온프레미스 계정계망
- VPN 기반 연결

---

# AWS 영역

## Public Subnet

- ALB
- Bastion Host
- Nginx

---

## Private App Subnet

- service-frontend
- service-backend
- service-ai-server
- mydata-server

---

# 온프레미스 영역

- bank-server
- stock-server
- transaction-server
- Kafka
- PostgreSQL

---

# 네트워크 연결

- Site-to-Site VPN(IPsec)
- pfSense + strongSwan 사용

---

# 보안 정책

- 금융 데이터는 온프레미스 보관
- 내부 서버 직접 외부 노출 금지
- Bastion Host 기반 접근
- Private Network 기반 통신

---

# 외부 공개 포트

| 포트  | 설명    |
|-----|-------|
| 80  | HTTP  |
| 443 | HTTPS |

---

# 내부 포트

| 서비스         | 포트   |
|-------------|------|
| Spring Boot | 8080 |
| FastAPI     | 8000 |
| PostgreSQL  | 5432 |
| Redis       | 6379 |
| Kafka       | 9092 |