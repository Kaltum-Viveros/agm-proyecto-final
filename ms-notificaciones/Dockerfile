# Usamos una imagen base oficial de Python ligera
FROM python:3.12-slim

# Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos solo el archivo de requerimientos primero (optimización de caché)
COPY requirements.txt .

# Instalamos las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código de la aplicación
COPY . .

# Exponemos los puertos (8006 para REST, 50056 para gRPC)
EXPOSE 8006 50056

# Comando para iniciar la aplicación:
# 1. Crea la carpeta si no existe
# 2. Genera los archivos de gRPC leyendo de la carpeta compartida /app/proto
# 3. Inicia uvicorn
CMD ["bash", "-c", "mkdir -p app/grpc/generated && touch app/grpc/generated/__init__.py && python -m grpc_tools.protoc -I=proto --python_out=app/grpc/generated --grpc_python_out=app/grpc/generated proto/notificaciones.proto && uvicorn app.main:app --host 0.0.0.0 --port 8006 --reload"]
