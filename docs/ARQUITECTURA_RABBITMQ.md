# Arquitectura RabbitMQ y fallback gRPC

Este documento describe la arquitectura actual de comunicacion interna del
proyecto AGM. AGM mantiene APIs REST hacia frontend/Postman y usa RabbitMQ como
middleware principal entre microservicios, conservando gRPC como canal de
fallback ante fallos de transporte.

## Arquitectura general

- REST se mantiene igual para comunicacion externa con frontend/Postman.
- RabbitMQ es el canal principal para comunicacion interna entre microservicios.
- gRPC se mantiene como canal secundario/fallback.
- Cada microservicio mantiene su propia base de datos.
- Docker Compose levanta RabbitMQ, microservicios y bases de datos.

Flujo principal:

```text
Frontend/Postman
   |
   | REST
   v
Microservicio origen
   |
   | RabbitMQ RPC principal
   v
RabbitMQ
   |
   v
Microservicio destino
```

Fallback:

```text
Microservicio origen -> gRPC directo -> Microservicio destino
```

## Modo hibrido

La variable `COMMUNICATION_MODE` controla el canal interno usado por los
clientes hibridos:

| Valor | Comportamiento |
| --- | --- |
| `grpc` | Usa solo gRPC. |
| `rabbit` | Usa solo RabbitMQ. |
| `hybrid` | Usa RabbitMQ como canal principal y gRPC como fallback ante errores de transporte. |

Modo recomendado:

```bash
COMMUNICATION_MODE=hybrid
```

El fallback aplica ante errores de transporte como timeout, conexion rechazada,
broker detenido, canal cerrado o errores equivalentes de RabbitMQ. No debe
usarse para ocultar errores de negocio validos como token invalido, materia no
encontrada, alumno no inscrito o listas vacias.

## Exchanges

| Exchange | Tipo | Uso |
| --- | --- | --- |
| `agm.rpc` | `direct` | Llamadas request/response entre microservicios. |
| `agm.events` | `topic` | Eventos asincronos para notificaciones. |

## Servicios expuestos por RabbitMQ

| Servicio | Cola | Proposito | Estado |
| --- | --- | --- | --- |
| MS-1 Auth | `auth.rpc.q` | Validacion de token, roles y usuarios | Implementado |
| MS-2 Periodos/Materias | `periodos_materias.rpc.q` | Consulta de materias, NRC, materias por docente y periodo activo | Implementado |
| MS-3 Docentes-Alumnos | `docentes_alumnos.rpc.q` | Consulta de alumnos, docentes, inscripciones y materias por alumno | Implementado |
| MS-4 Calificaciones | `calificaciones.rpc.q` | Concentrado, promedio de alumno y estadisticas de materia | Implementado |
| MS-5 Asistencias | `asistencias.rpc.q` | Asistencia por alumno, asistencias por materia y estadisticas de asistencia | Implementado |
| MS-6 Notificaciones | `notificaciones.events.q` | Procesamiento de correos mediante eventos RabbitMQ | Implementado como consumidor de eventos |
| MS-7 Reportes | Sin cola propia todavia | Consume Auth, Periodos, Docentes, Calificaciones y Asistencias por RabbitMQ | Consumidor hibrido |

## Routing keys RPC

### Auth

- `rpc.auth.validate_token`
- `rpc.auth.check_role`
- `rpc.auth.get_user_by_id`
- `rpc.auth.create_or_get_user_identity`

### Periodos/Materias

- `rpc.periodos.get_materia_by_id`
- `rpc.periodos.get_materia_by_nrc`
- `rpc.periodos.get_materias_by_docente`
- `rpc.periodos.get_periodo_activo`

### Docentes-Alumnos

- `rpc.docentes.get_alumnos_by_materia`
- `rpc.docentes.is_alumno_en_materia`
- `rpc.docentes.get_materias_by_alumno`
- `rpc.docentes.get_alumno_by_id`
- `rpc.docentes.get_docente_by_id`
- `rpc.docentes.get_docente_by_nombre`
- `rpc.docentes.get_docente_by_email`
- `rpc.docentes.get_alumno_by_email`

### Calificaciones

- `rpc.calificaciones.get_concentrado`
- `rpc.calificaciones.get_promedio_alumno`
- `rpc.calificaciones.get_estadisticas_materia`

### Asistencias

- `rpc.asistencias.get_asistencia_alumno`
- `rpc.asistencias.get_asistencias_materia`
- `rpc.asistencias.get_estadisticas_asistencia`

## Eventos de notificaciones

MS-6 Notificaciones consume eventos desde `agm.events` mediante la cola
`notificaciones.events.q`.

- `event.notificaciones.bienvenida_alumno`
- `event.notificaciones.baja_alumno`
- `event.notificaciones.cierre_materia`
- `event.notificaciones.reset_password`

Los productores reales de estos eventos todavia no fueron migrados. Los flujos
existentes por gRPC/REST siguen activos.

## RabbitMQ UI

RabbitMQ Management UI:

- URL: `http://localhost:15673`
- Credenciales: `agm / agm_password`

Dentro de Docker, el puerto AMQP sigue siendo `5672` y los servicios usan:

```bash
RABBITMQ_URL=amqp://agm:agm_password@rabbitmq:5672/
```

En host, el puerto AMQP puede publicarse como `5673` si existe conflicto local.
Revisa el valor efectivo con:

```bash
docker compose ps rabbitmq
```

## Comandos basicos

Levantar RabbitMQ:

```bash
docker compose up -d rabbitmq
```

Levantar todo:

```bash
docker compose up -d
```

Ver logs:

```bash
docker compose logs --tail=100 rabbitmq
docker compose logs --tail=100 ms-auth
docker compose logs --tail=100 ms-periodos-materias
docker compose logs --tail=100 ms-docentes-alumnos
docker compose logs --tail=100 ms-calificaciones
docker compose logs --tail=100 ms-asistencias
docker compose logs --tail=100 ms-notificaciones
docker compose logs --tail=100 ms-reportes
```

## Scripts de prueba

Scripts RabbitMQ existentes:

```bash
docker compose exec -T ms-auth python scripts/test_auth_rabbit_rpc.py
docker compose exec -T ms-periodos-materias python scripts/test_periodos_rabbit_rpc.py
docker compose exec -T ms-docentes-alumnos python scripts/test_docentes_rabbit_rpc.py
docker compose exec -T ms-calificaciones python scripts/test_calificaciones_rabbit_rpc.py
docker compose exec -T ms-asistencias python scripts/test_asistencias_rabbit_rpc.py
docker compose exec -T ms-notificaciones python scripts/test_notification_events.py
```

Tambien existen scripts puntuales de clientes hibridos en algunos servicios para
validar integraciones especificas.

## Probar fallback gRPC

1. Levantar servicios:

```bash
docker compose up -d rabbitmq ms-auth ms-periodos-materias ms-docentes-alumnos ms-calificaciones ms-asistencias ms-notificaciones ms-reportes
```

2. Probar un endpoint REST normal que dependa de comunicacion interna.

3. Apagar RabbitMQ:

```bash
docker compose stop rabbitmq
```

4. Repetir el mismo endpoint.

5. Verificar logs. Debe aparecer un mensaje similar a:

```text
RabbitMQ RPC failed, falling back to gRPC
```

6. Volver a levantar RabbitMQ:

```bash
docker compose up -d rabbitmq
```

No dejar RabbitMQ detenido al terminar pruebas.

## Estado actual de implementacion

Implementado:

- RabbitMQ en Docker Compose.
- Infraestructura compartida de mensajeria.
- Contratos y routing keys.
- Auth expuesto por RabbitMQ RPC.
- Periodos/Materias expuesto por RabbitMQ RPC.
- Docentes-Alumnos expuesto por RabbitMQ RPC.
- Calificaciones expuesto por RabbitMQ RPC.
- Asistencias expuesto por RabbitMQ RPC.
- Reportes consume Auth, Periodos, Docentes, Calificaciones y Asistencias mediante RabbitMQ con fallback gRPC.
- Notificaciones consume eventos RabbitMQ.
- gRPC se mantiene como fallback.
- REST hacia frontend no cambio.

Pendiente:

- Migrar productores reales de eventos de notificacion.
- Corregir flujo de bienvenida docente si sigue pendiente.
- Agregar pruebas de integracion automatizadas.
- Agregar resiliencia avanzada como DLQ/retry si se requiere.

## Decisiones tecnicas

- Se mantuvo gRPC porque ya funcionaba y sirve como fallback mientras RabbitMQ
  se adopta de forma gradual.
- RabbitMQ reduce el acoplamiento directo entre servicios y centraliza la
  comunicacion interna.
- El modo hibrido permite migrar consumidores y proveedores por etapas sin
  romper REST ni los flujos existentes.
- Notificaciones por eventos desacopla el envio de correos del flujo principal
  y permite procesamiento asincrono.

## Restricciones vigentes

- No eliminar gRPC mientras siga siendo fallback.
- No cambiar endpoints REST por cambios de mensajeria interna.
- No modificar archivos `.proto` para agregar routing keys RabbitMQ.
- No usar fallback gRPC para errores de negocio validos.
