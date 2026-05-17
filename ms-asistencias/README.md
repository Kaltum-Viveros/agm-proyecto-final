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

## 🔒 Seguridad, Roles (RBAC) y Extracción de JWT
El microservicio implementa un sistema descentralizado de seguridad y RBAC:
- **Middleware JWT:** Se utiliza `HTTPBearer` en `app/core/security.py` para interceptar cada petición HTTP.
- **Validación via gRPC:** Se consulta a **MS-Auth (MS-1)** a través de gRPC para validar la firma, expiración y estado del token.
- **Claims y Roles Locales:** De los claims válidos se extrae el rol y los identificadores seguros (`id_docente` o `id_alumno`), evitando que el cliente mande IDs en el cuerpo de la petición.
  - `requerir_docente`: Permite el acceso únicamente a usuarios con rol `DOCENTE` o `ADMINISTRADOR`.
  - `requerir_alumno`: Permite el acceso únicamente a usuarios con rol `ALUMNO`.
  - `requerir_usuario`: Permite el acceso a cualquier usuario con token JWT activo.

## ⚙️ Flujos y Validaciones de Negocio (Fase 14)
El microservicio aplica **Arquitectura Limpia** delegando el 100% de la lógica a la capa de servicios (`services/`), manteniendo los routers REST delgados:
1. **Iniciar Sesión (`POST /sesiones/iniciar`):**
   - Extrae el `id_docente` desde las claims del JWT.
   - Consulta al **MS-2 (Materias)** mediante gRPC para validar que el docente tenga asignada la materia. Si no es así, lanza `403 Forbidden`.
   - Si el MS-2 no responde, maneja la excepción y lanza `503 Service Unavailable`.
   - Comprueba si existe una sesión activa para esa materia en la BD local (`409 Conflict`).
   - Crea la sesión con una duración automática de 10 minutos.
2. **Generar QR (`POST /qr/generar`):**
   - Extrae el `id_alumno` y su matrícula desde el JWT de forma transparente.
   - Busca la sesión localmente (`404 Not Found` si no existe).
   - Comprueba que la sesión esté `ACTIVA` y no haya expirado (`409 Conflict`).
   - Consulta al **MS-3 (Alumnos)** mediante gRPC para verificar que el alumno curse dicha materia. Si no, lanza `403 Forbidden`.
   - Si el MS-3 está caído, responde con `503 Service Unavailable`.
   - Cifra el código QR usando Fernet e introduce un UUID como nonce para evitar ataques de repetición (Anti-Replay).

## 🔒 Flujo de Seguridad QR (Anti-Replay)
1. El alumno solicita un QR. El MS-5 genera un payload con `id_alumno`, `id_sesion` y un `uuid` único. Este payload se cifra usando `cryptography.fernet` y se devuelve al alumno.
2. El alumno muestra el QR en pantalla (válido por 20 segundos).
3. El docente escanea el QR. Se envía el string cifrado al MS-5.
4. El MS-5 calcula la huella (SHA-256) del QR y verifica que no exista en la tabla `tokens_qr_usados`.
5. Si es válido, se descifra, se comprueba el tiempo y se registra la asistencia como PRESENTE o RETARDO dependiendo de `fecha_hora_limite_presente` de la sesión.

## 🧪 Pruebas Automatizadas
El microservicio incluye una suite de pruebas unitarias y de integración que aíslan el servicio utilizando Mocks para llamadas externas de gRPC y base de datos:
```bash
# Correr todas las pruebas locales
pytest

# Correr pruebas dentro del contenedor de Docker
docker-compose exec ms-asistencias pytest
```
La suite incluye:
- `test_health.py`: Verifica el estado y disponibilidad de la API REST.
- `test_sessions.py`: Pruebas de integración de la lógica de negocio para iniciar sesiones (flujos felices, 403, 503).
- `test_qr.py`: Valida los flujos de generación de código QR (flujo feliz, 404, 409, 403).
- `test_grpc.py`: Prueba de integración real de gRPC entrante contra el puerto local `50055`.

