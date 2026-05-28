FROM python:3.11-slim AS builder

WORKDIR /app

COPY requirements.txt .

# 💡 gcc 및 빌드에 필요한 패키지 설치 추가
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# CPU-only torch 먼저 설치해서 CUDA 버전(~2GB) 대신 CPU 버전(~200MB) 사용
RUN pip install --no-cache-dir \
    --prefix=/install \
    torch --index-url https://download.pytorch.org/whl/cpu

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