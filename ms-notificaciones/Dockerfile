# Usamos una imagen base oficial de Python ligera
FROM python:3.12-slim

# Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos solo el archivo de requerimientos primero (optimización de caché)
COPY requirements.txt .

# Instalamos las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código de la aplicación
# NOTA IMPORTANTE (proto stubs):
#   Los archivos generados de gRPC (app/grpc/generated/*.py) están versionados en el repositorio
#   y se copian aquí directamente. NO se recompilan dentro de la imagen por las siguientes razones:
#   1. Docker no puede hacer COPY ../proto si el build context es ms-notificaciones/
#   2. El volumen ./proto:/app/proto del docker-compose SOLO está disponible en runtime (no en build)
#   3. Los stubs generados son estables y se recompilan manualmente con:
#      python -m grpc_tools.protoc -I=../proto --python_out=app/grpc/generated \
#             --grpc_python_out=app/grpc/generated ../proto/*.proto
#   Si se modifican los .proto, correr el comando anterior en local y commitear los stubs resultantes.
COPY . .

# Exponemos los puertos:
#   8006 → REST (FastAPI/Uvicorn)
#   50056 → gRPC (servidor interno)
# NOTA DE SEGURIDAD gRPC:
#   El servidor gRPC usa add_insecure_port, apropiado ÚNICAMENTE para la red interna Docker.
#   En producción real sobre redes públicas o multi-zona, implementar mTLS/TLS.
EXPOSE 8006 50056

# Comando para iniciar la aplicación:
#   - python -m app.grpc.server: levanta el servidor gRPC de MS-6 en segundo plano
#   - uvicorn: levanta el servidor REST en primer plano
CMD ["bash", "-c", "python -m app.grpc.server & uvicorn app.main:app --host 0.0.0.0 --port 8006"]
