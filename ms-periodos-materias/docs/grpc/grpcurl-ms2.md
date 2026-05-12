# MS-2 Periodos y Materias — Pruebas gRPC con grpcurl

Este documento muestra cómo consumir el servidor gRPC del microservicio MS-2 usando `grpcurl`.

---

## Puertos

| Entorno       | Dirección                          |
|---------------|------------------------------------|
| REST          | `localhost:8002`                   |
| gRPC          | `localhost:50052`                  |
| Dentro de Docker | `ms-periodos-materias-api:50052` |

---

## Contrato proto

El contrato gRPC usado por MS-2 se encuentra en:

```
../proto/periodos_materias.proto
```

El servicio expuesto es:

```
agm.periodos_materias.v1.PeriodosMateriasService
```

---

## Listar servicios disponibles

Desde la carpeta `ms-periodos-materias`:

```bash
docker run --rm -v "%cd%\..\proto:/proto" fullstorydev/grpcurl \
  -plaintext -import-path /proto -proto periodos_materias.proto \
  host.docker.internal:50052 list
```

Resultado esperado:

```
agm.periodos_materias.v1.PeriodosMateriasService
```

---

## Describir el servicio

```bash
docker run --rm -v "%cd%\..\proto:/proto" fullstorydev/grpcurl \
  -plaintext -import-path /proto -proto periodos_materias.proto \
  host.docker.internal:50052 describe agm.periodos_materias.v1.PeriodosMateriasService
```

Métodos disponibles:

- `GetMateriaById`
- `GetMateriasByDocente`
- `GetPeriodoActivo`

---

## Obtener periodo activo

```bash
docker run --rm -v "%cd%\..\proto:/proto" fullstorydev/grpcurl \
  -plaintext -import-path /proto -proto periodos_materias.proto \
  -d "{}" \
  host.docker.internal:50052 agm.periodos_materias.v1.PeriodosMateriasService/GetPeriodoActivo
```

---

## Obtener materia por ID

Reemplazar `UUID_DE_MATERIA_OFERTADA` por un UUID real de `materias_ofertadas`.

```bash
docker run --rm -v "%cd%\..\proto:/proto" fullstorydev/grpcurl \
  -plaintext -import-path /proto -proto periodos_materias.proto \
  -d "{\"materia_id\":\"UUID_DE_MATERIA_OFERTADA\"}" \
  host.docker.internal:50052 agm.periodos_materias.v1.PeriodosMateriasService/GetMateriaById
```

---

## Obtener materias por docente

Reemplazar `UUID_DE_DOCENTE` por el UUID externo del docente proveniente de MS-3.

```bash
docker run --rm -v "%cd%\..\proto:/proto" fullstorydev/grpcurl \
  -plaintext -import-path /proto -proto periodos_materias.proto \
  -d "{\"docente_id\":\"UUID_DE_DOCENTE\"}" \
  host.docker.internal:50052 agm.periodos_materias.v1.PeriodosMateriasService/GetMateriasByDocente
```

---

## Nota sobre `docente_id`

El campo `docente_id` pertenece al microservicio **MS-3 Docentes y Alumnos**.

- MS-2 únicamente almacena el UUID externo para relacionar materias ofertadas con docentes.
- MS-2 no valida actualmente ese UUID contra la base de datos de MS-3.
- Esa validación se integrará posteriormente por gRPC cuando MS-3 esté disponible.