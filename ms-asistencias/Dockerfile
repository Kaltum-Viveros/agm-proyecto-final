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
COPY requirements.txt .

# Instalar las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código del microservicio
COPY . .

# Exponer los puertos:
# 8005 -> REST (FastAPI)
# 50055 -> gRPC
EXPOSE 8005 50055

# Comando por defecto para iniciar FastAPI y gRPC 
# (En producción, idealmente se levantan en procesos separados o mediante un script de inicio)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8005 & python -m app.grpc_server.asistencias_server"]
