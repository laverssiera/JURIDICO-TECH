FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV WORKER_DATABASE_URL=postgresql+asyncpg://juridico:juridico@postgres:5432/juridico
ENV WORKER_NATS_URL=nats://nats:4222
ENV WORKER_POLL_INTERVAL=5
ENV WORKER_MAX_ATTEMPTS=5
ENV WORKER_BATCH_SIZE=50

CMD ["uvicorn", "worker.main:app", "--host", "0.0.0.0", "--port", "8001"]
