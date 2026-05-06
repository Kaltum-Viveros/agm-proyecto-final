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
# se expone el puerto 8002 para que el servicio sea accesible desde fuera del contenedor
EXPOSE 8002
# levantamos el servicio usando uvicorn, especificando el host y el puerto 
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]