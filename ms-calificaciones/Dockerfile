FROM python:3.11-slim

WORKDIR /app

COPY shared ./shared
COPY ms-calificaciones/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ms-calificaciones/app ./app
COPY ms-calificaciones/alembic ./alembic
COPY ms-calificaciones/alembic.ini .
COPY ms-calificaciones/proto ./proto
COPY ms-calificaciones/scripts ./scripts

EXPOSE 8004 50054

CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8004"]