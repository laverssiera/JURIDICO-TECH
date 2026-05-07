FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV LEGAL_AI_DATABASE_URL=postgresql+asyncpg://juridico:juridico@postgres:5432/juridico
ENV LEGAL_AI_OPENAI_API_KEY=""
ENV LEGAL_AI_EMBEDDING_MODEL=text-embedding-3-small
ENV LEGAL_AI_CHAT_MODEL=gpt-4o-mini

CMD ["uvicorn", "legal_ai.main:app", "--host", "0.0.0.0", "--port", "8002"]
