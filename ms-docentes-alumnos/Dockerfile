# 1. Usamos una imagen de Python ligera
FROM python:3.11-slim

# 2. Evitar que Python genere archivos .pyc y permitir logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Establecer el directorio de trabajo
WORKDIR /app

# 4. Instalar dependencias del sistema necesarias para Postgres y compilación
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 5. Copiar e instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copiar el resto del código
COPY . .

# 7. Comando para arrancar la app
CMD python grpc_server.py & uvicorn app.main:app --host 0.0.0.0 --port 8003