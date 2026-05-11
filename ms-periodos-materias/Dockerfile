# se usa python 3.12 
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
#crea el directorio de la aplicación dentro del contenedor
WORKDIR /app
# instala las dependencias del proyecto
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt
# se copia el código de la aplicación al contenedor
COPY app ./app
# se copia el archivo de configuración de Alembic y el directorio de migraciones al contenedor
COPY alembic.ini .
# se copia el directorio de migraciones de Alembic al contenedor
COPY alembic ./alembic
# se copia el script de ejecución del servicio al contenedor
COPY run.py .
# se expone el puerto 8002 para que el servicio sea accesible desde fuera del contenedor y el puerto 50052 para gRPC
EXPOSE 8002 50052
# levantamos el servicio usando uvicorn, especificando el host y el puerto 
CMD ["python", "run.py"]