FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api/ ./api/
COPY alembic.ini .
COPY alembic/ ./alembic/
COPY scripts/ ./scripts/

ENV PYTHONPATH=/app
ENV PORT=8000

CMD uvicorn api.main:app --host 0.0.0.0 --port $PORT
