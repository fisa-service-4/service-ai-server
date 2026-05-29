FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .

# 💡 gcc 및 빌드에 필요한 패키지 설치 추가
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    --prefix=/install \
    -r requirements.txt

COPY . .

FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /install /usr/local
COPY --from=builder /app .

EXPOSE 8000

CMD ["uvicorn","src.main:app","--host","0.0.0.0","--port","8000"]