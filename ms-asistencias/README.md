# MS-5: Microservicio de Asistencias QR

Este microservicio se encarga de la gestión de pases de lista mediante códigos QR dinámicos para el Sistema de Gestión y Automatización de Calificaciones (AGM).

## 🚀 Tecnologías
- **Framework REST:** FastAPI
- **Comunicación Interna:** gRPC (Protocol Buffers)
- **Base de Datos:** PostgreSQL (AsyncPG) + SQLAlchemy 2.0
- **Migraciones:** Alembic
- **Pruebas:** Pytest
- **Despliegue:** Docker

## 📂 Estructura del Proyecto
El microservicio sigue una Arquitectura Limpia (Clean Architecture) dividida en:
- `api/`: Endpoints expuestos mediante FastAPI.
- `core/`: Configuraciones globales y variables de entorno.
- `db/`: Conexión a la base de datos asíncrona.
- `generated/`: Código autogenerado por gRPC.
- `grpc_server/`: Servidor gRPC para comunicación interna.
- `models/`: Modelos ORM de SQLAlchemy.
- `repositories/`: Capa de abstracción de base de datos (queries).
- `schemas/`: Esquemas de Pydantic para validación de datos (Input/Output).
- `services/`: Lógica de negocio (Criptografía QR, cálculo de retardos).

## ⚙️ Puertos
- **REST (FastAPI):** 8005
- **gRPC:** 50055

## 🔧 Variables de Entorno (.env)
Copie el archivo `.env.example` a `.env` y configure:
```ini
ENVIRONMENT=local
DATABASE_URL=postgresql+asyncpg://agm_user:agm_password@localhost:5432/agm_asistencias_db
QR_SECRET_KEY=TU_CLAVE_BASE64_AQUI
QR_TTL_SECONDS=20
SESSION_DURATION_MINUTES=10
PRESENT_LIMIT_MINUTES=5
```

## 🛠 Instalación Local
1. Instalar dependencias: `pip install -r requirements.txt`
2. Aplicar migraciones: `alembic upgrade head`
3. Ejecutar servidor REST: `uvicorn app.main:app --reload --port 8005`
4. Ejecutar servidor gRPC: `python -m app.grpc_server.asistencias_server`

## 🐳 Despliegue con Docker
Desde la raíz del proyecto (donde está el `docker-compose.yml`):
```bash
docker-compose up -d ms-asistencias
```

## 🔒 Flujo de Seguridad QR (Anti-Replay)
1. El alumno solicita un QR. El MS-5 genera un payload con `id_alumno`, `id_sesion` y un `uuid` único. Este payload se cifra usando `cryptography.fernet` y se devuelve al alumno.
2. El alumno muestra el QR en pantalla (válido por 20 segundos).
3. El docente escanea el QR. Se envía el string cifrado al MS-5.
4. El MS-5 calcula la huella (SHA-256) del QR y verifica que no exista en la tabla `tokens_qr_usados`.
5. Si es válido, se descifra, se comprueba el tiempo y se registra la asistencia como PRESENTE o RETARDO dependiendo de `fecha_hora_limite_presente` de la sesión.
