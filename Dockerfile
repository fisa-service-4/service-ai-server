FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
 && rm -rf /var/lib/apt/lists/*

<<<<<<< Updated upstream
RUN pip install --no-cache-dir \
=======
COPY requirements.txt .

RUN pip install --upgrade pip

RUN pip install \
    --no-cache-dir \
>>>>>>> Stashed changes
    --prefix=/install \
    -r requirements.txt

FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY --from=builder /install /usr/local

COPY src ./src
COPY requirements.txt .

EXPOSE 8000

CMD ["uvicorn","src.main:app","--host","0.0.0.0","--port","8000"]