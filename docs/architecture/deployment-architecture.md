# deployment-architecture.md

# Deployment Architecture

# 배포 환경

- Docker 기반 컨테이너 배포
- AWS EC2 기반 서비스 운영
- 온프레미스 서버 별도 운영

---

# AWS 배포 구성

| 서비스               | 배포 위치 |
|-------------------|-------|
| service-frontend  | EC2   |
| service-backend   | EC2   |
| service-ai-server | EC2   |
| mydata-server     | EC2   |

---

# 온프레미스 배포 구성

| 서비스                | 배포 위치    |
|--------------------|----------|
| bank-server        | 온프레미스 서버 |
| stock-server       | 온프레미스 서버 |
| transaction-server | 온프레미스 서버 |
| Kafka              | 온프레미스 서버 |

---

# 배포 프로세스

1. GitHub Push
2. Jenkins Pipeline 실행
3. Docker Image Build
4. SonarQube 분석
5. Docker Compose 배포

---

# Reverse Proxy

- Nginx 사용
- HTTPS 종단 처리
- API 라우팅 처리

---

# CI/CD

## Jenkins

- PR 빌드
- 테스트 실행
- Docker Build
- 배포 자동화

---

# 코드 품질

## SonarQube

- 정적 분석
- Quality Gate 적용

---

# 컨테이너 관리

## Docker Compose

- local
- dev
- prod

환경 분리 운영