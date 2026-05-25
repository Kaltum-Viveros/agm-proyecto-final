FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY shared ./shared
COPY ms-auth/requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY ms-auth/app ./app
COPY ms-auth/scripts ./scripts
COPY ms-auth/alembic.ini .
COPY ms-auth/alembic ./alembic

EXPOSE 8001
EXPOSE 50051

CMD ["python", "-m", "app.start"]