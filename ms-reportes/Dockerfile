FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# Dependencias del sistema para asyncpg y compilación C
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY shared ./shared
COPY ms-reportes/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ms-reportes/app ./app
COPY ms-reportes/alembic ./alembic
COPY ms-reportes/alembic.ini .

# 8007 -> REST (FastAPI)
# 50057 -> gRPC
EXPOSE 8007 50057

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8007"]
