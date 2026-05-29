# Usamos una imagen oficial de Python ligera
FROM python:3.11-slim

# Establecemos variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalar dependencias del sistema requeridas para asyncpg y grpc
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar solo el requirements primero para aprovechar el caché de Docker
COPY shared ./shared
COPY ms-asistencias/requirements.txt .

# Instalar las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código del microservicio
COPY ms-asistencias/app ./app
COPY ms-asistencias/alembic ./alembic
COPY ms-asistencias/alembic.ini .
COPY ms-asistencias/run.py .
COPY ms-asistencias/scripts ./scripts
COPY ms-asistencias/tests ./tests

# Exponer los puertos:
# 8005 -> REST (FastAPI)
# 50055 -> gRPC
EXPOSE 8005 50055

# Comando por defecto para iniciar la API REST usando Gunicorn con workers de Uvicorn
CMD ["sh", "-c", "alembic upgrade head && python -m app.grpc_server.asistencias_server & gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8005 app.main:app"]
