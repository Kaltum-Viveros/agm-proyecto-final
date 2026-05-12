## Integración con otros microservicios

MS-2 expone dos interfaces:

- REST API: `http://localhost:8002`
- gRPC: `localhost:50052`

Dentro de Docker, otros servicios pueden consumir MS-2 usando el nombre del servicio:

- REST: `http://ms-periodos-materias-api:8002`
- gRPC: `ms-periodos-materias-api:50052`

### Endpoints REST principales

- `GET /api/v1/health`
- `GET /api/v1/health/db`
- `GET /api/v1/periodos/activo`
- `GET /api/v1/materias`
- `GET /api/v1/materias/{materia_ofertada_id}`
- `GET /api/v1/materias/docente/{docente_id}`
- `GET /api/v1/materias/periodo/{periodo_id}`
- `GET /api/v1/materias/periodo-activo`

### Métodos gRPC disponibles

Servicio:

```txt
agm.periodos_materias.v1.PeriodosMateriasService
```

### Métodos

- `GetMateriaById`
- `GetMateriasByDocente`
- `GetPeriodoActivo`

### Nota sobre docente_id

El campo `docente_id` pertenece al MS-3 Docentes y Alumnos.

MS-2 guarda el UUID externo del docente, pero no valida su existencia contra la base de datos de MS-3. Esa validación se integrará posteriormente mediante gRPC cuando MS-3 esté disponible.