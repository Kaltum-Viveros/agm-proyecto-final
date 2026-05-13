# MS-2 Periodos y Materias

Microservicio encargado de administrar periodos académicos, planes de estudio, materias catálogo, materias ofertadas, horarios e importación de programación académica desde PDF.

---

## Puertos

| Protocolo           | Puerto |
|---------------------|--------|
| REST                | 8002   |
| gRPC                | 50052  |
| PostgreSQL (host)   | 5433   |
| PostgreSQL (Docker) | 5432   |

---

## Base de datos

MS-2 usa una base de datos PostgreSQL propia.

- **Nombre:** `agm_periodos_db`
- **Contenedor:** `ms-periodos-materias-db`

El microservicio mantiene independencia de base de datos respecto a otros servicios.

---

## Levantar el servicio

Desde la carpeta `ms-periodos-materias`:

```bash
docker compose up -d --build
```

Ver contenedores:

```bash
docker compose ps
```

Ver logs:

```bash
docker compose logs -f ms-periodos-materias-api
```

Detener contenedores:

```bash
docker compose down
```

---

## Migraciones Alembic

Ejecutar migraciones:

```bash
docker compose exec ms-periodos-materias-api alembic upgrade head
```

Ver historial:

```bash
docker compose exec ms-periodos-materias-api alembic history
```

Crear nueva migración:

```bash
docker compose exec ms-periodos-materias-api alembic revision --autogenerate -m "descripcion"
```

---

## Pruebas

Ejecutar toda la suite:

```bash
docker compose exec ms-periodos-materias-api pytest
```

Resultado esperado actual: **55 passed**

---

## Health checks

Verificar API:

```bash
curl http://localhost:8002/api/v1/health
```

Verificar base de datos:

```bash
curl http://localhost:8002/api/v1/health/db
```

---

## Swagger y OpenAPI

- **Swagger UI:** http://localhost:8002/docs
- **OpenAPI JSON:** http://localhost:8002/openapi.json
- **Archivo exportado:** `docs/openapi/ms-2-openapi.json`

---

## Endpoints REST principales

### Health

```
GET  /api/v1/health
GET  /api/v1/health/db
```

### Periodos

```
GET    /api/v1/periodos
POST   /api/v1/periodos
GET    /api/v1/periodos/activo
GET    /api/v1/periodos/{periodo_id}
PATCH  /api/v1/periodos/{periodo_id}
PATCH  /api/v1/periodos/{periodo_id}/activar
DELETE /api/v1/periodos/{periodo_id}
```

### Planes de estudio

```
GET    /api/v1/planes-estudio
POST   /api/v1/planes-estudio
GET    /api/v1/planes-estudio/{plan_estudio_id}
PATCH  /api/v1/planes-estudio/{plan_estudio_id}
DELETE /api/v1/planes-estudio/{plan_estudio_id}
```

### Materias catálogo

```
GET    /api/v1/materias-catalogo
POST   /api/v1/materias-catalogo
GET    /api/v1/materias-catalogo/{materia_catalogo_id}
PATCH  /api/v1/materias-catalogo/{materia_catalogo_id}
DELETE /api/v1/materias-catalogo/{materia_catalogo_id}
```

### Materias y planes de estudio

```
GET    /api/v1/materias-planes-estudio
POST   /api/v1/materias-planes-estudio
GET    /api/v1/materias-planes-estudio/{materia_plan_estudio_id}
PATCH  /api/v1/materias-planes-estudio/{materia_plan_estudio_id}
DELETE /api/v1/materias-planes-estudio/{materia_plan_estudio_id}
```

### Materias ofertadas

```
GET    /api/v1/materias-ofertadas
POST   /api/v1/materias-ofertadas
GET    /api/v1/materias-ofertadas/{materia_ofertada_id}
PATCH  /api/v1/materias-ofertadas/{materia_ofertada_id}
PATCH  /api/v1/materias-ofertadas/{materia_ofertada_id}/activar
PATCH  /api/v1/materias-ofertadas/{materia_ofertada_id}/cerrar
PATCH  /api/v1/materias-ofertadas/{materia_ofertada_id}/cancelar
PATCH  /api/v1/materias-ofertadas/{materia_ofertada_id}/asignar-docente
DELETE /api/v1/materias-ofertadas/{materia_ofertada_id}
```

### Horarios

```
GET    /api/v1/materia-horarios
POST   /api/v1/materia-horarios
GET    /api/v1/materia-horarios/{materia_horario_id}
PATCH  /api/v1/materia-horarios/{materia_horario_id}
DELETE /api/v1/materia-horarios/{materia_horario_id}
```

### Materias académicas

```
GET /api/v1/materias
GET /api/v1/materias/{materia_ofertada_id}
GET /api/v1/materias/docente/{docente_id}
GET /api/v1/materias/periodo/{periodo_id}
GET /api/v1/materias/periodo-activo
```

### Importación PDF

```
POST /api/v1/importaciones/programacion-academica
```

---

## Paginación

Los endpoints de lista aceptan los parámetros `page` y `limit`.

Ejemplo:

```bash
curl "http://localhost:8002/api/v1/materias?page=1&limit=10"
```

Respuesta estándar:

```json
{
  "success": true,
  "data": {
    "items": [],
    "total": 0,
    "page": 1,
    "limit": 10,
    "pages": 0
  },
  "message": "Registros obtenidos correctamente"
}
```

---

## Flujo de importación PDF

- **Endpoint:** `POST /api/v1/importaciones/programacion-academica`
- **Tipo de envío:** `multipart/form-data`

**Campos requeridos:**

| Campo              | Descripción              |
|--------------------|--------------------------|
| `periodo_id`       | ID del periodo           |
| `plan_estudio_id`  | ID del plan de estudio   |
| `archivo`          | Archivo PDF              |

**Datos extraídos del PDF:**

- NRC
- Clave
- Materia
- Sección
- Días
- Hora
- Profesor
- Salón

**La información se guarda en:**

- `materias_catalogo`
- `materia_plan_estudio`
- `materias_ofertadas`
- `materia_horarios`

> Si una materia ya existe para el mismo periodo y NRC, se evita duplicar la materia ofertada. Al reimportar, los horarios se reemplazan para mantener la programación actualizada.

---

## gRPC

- **Puerto:** `50052`
- **Servicio:** `agm.periodos_materias.v1.PeriodosMateriasService`

**Métodos disponibles:**

- `GetMateriaById`
- `GetMateriasByDocente`
- `GetPeriodoActivo`

### Listar servicio

```bash
docker run --rm -v "%cd%\..\proto:/proto" fullstorydev/grpcurl \
  -plaintext -import-path /proto -proto periodos_materias.proto \
  host.docker.internal:50052 list
```

### Obtener periodo activo

```bash
docker run --rm -v "%cd%\..\proto:/proto" fullstorydev/grpcurl \
  -plaintext -import-path /proto -proto periodos_materias.proto \
  -d "{}" \
  host.docker.internal:50052 agm.periodos_materias.v1.PeriodosMateriasService/GetPeriodoActivo
```

### Obtener materia por ID

```bash
docker run --rm -v "%cd%\..\proto:/proto" fullstorydev/grpcurl \
  -plaintext -import-path /proto -proto periodos_materias.proto \
  -d "{\"materia_id\":\"UUID_DE_MATERIA_OFERTADA\"}" \
  host.docker.internal:50052 agm.periodos_materias.v1.PeriodosMateriasService/GetMateriaById
```

### Obtener materias por docente

```bash
docker run --rm -v "%cd%\..\proto:/proto" fullstorydev/grpcurl \
  -plaintext -import-path /proto -proto periodos_materias.proto \
  -d "{\"docente_id\":\"UUID_DE_DOCENTE\"}" \
  host.docker.internal:50052 agm.periodos_materias.v1.PeriodosMateriasService/GetMateriasByDocente
```

---

## Despliegue individual

MS-2 puede ejecutarse en modo producción usando:

```bash
docker compose -f compose.prod.yml --env-file .env.production up -d --build
```

Antes de ejecutar, crear el archivo `.env.production` a partir del ejemplo.

En Windows:

```bash
copy .env.production.example .env.production
```

En Linux o macOS:

```bash
cp .env.production.example .env.production
```

Aplicar migraciones:

```bash
docker compose -f compose.prod.yml --env-file .env.production exec ms-periodos-materias-api alembic upgrade head
```

Verificar API REST:

```bash
curl http://localhost:8002/api/v1/health
```

Verificar base de datos:

```bash
curl http://localhost:8002/api/v1/health/db
```

Verificar gRPC:

```bash
docker run --rm -v "%cd%\..\proto:/proto" fullstorydev/grpcurl \
  -plaintext -import-path /proto -proto periodos_materias.proto \
  host.docker.internal:50052 list
```

Detener despliegue:

```bash
docker compose -f compose.prod.yml --env-file .env.production down
```

> Este compose no monta volúmenes de código fuente. La imagen contiene el código del microservicio, por lo que representa mejor un ambiente de despliegue.

---

## Nota sobre `docente_id`

El campo `docente_id` es un UUID externo del microservicio **MS-3 Docentes y Alumnos**.

- MS-2 **no** administra docentes en su propia base de datos.
- MS-2 almacena `docente_id` y `docente_nombre` para relacionar materias ofertadas con docentes.
- La validación real del docente contra MS-3 se integrará posteriormente mediante gRPC.