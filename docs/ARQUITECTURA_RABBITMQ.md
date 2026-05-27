# Arquitectura RabbitMQ y fallback gRPC

AGM es una plataforma de gestion escolar basada en microservicios. La
comunicacion externa hacia frontend/Postman sigue siendo REST, mientras que la
comunicacion interna entre microservicios usa RabbitMQ como canal principal y
conserva gRPC como fallback ante fallos de transporte.

El modo recomendado para el entorno actual es:

```bash
COMMUNICATION_MODE=hybrid
```

## Resumen de arquitectura

- RabbitMQ es el canal principal para comunicacion interna.
- gRPC se conserva como canal secundario/fallback.
- REST hacia frontend/Postman no cambio.
- Cada microservicio conserva su propia base de datos.
- Docker Compose levanta RabbitMQ, microservicios y bases de datos.

Flujo principal:

```text
Frontend/Postman
  | REST
  v
Microservicios
  | RabbitMQ RPC principal
  v
RabbitMQ
  v
Microservicio destino
```

Fallback:

```text
Microservicio origen -> gRPC directo -> Microservicio destino
```

## Componentes RabbitMQ

| Exchange | Tipo | Uso |
| --- | --- | --- |
| `agm.rpc` | `direct` | Llamadas RPC request/response entre microservicios. |
| `agm.events` | `topic` | Eventos asincronos de notificaciones. |
| `agm.events.dlx` | `direct` | Dead Letter Exchange para eventos fallidos. |

## Colas actuales

| Servicio | Cola | Tipo | Proposito | Estado |
| --- | --- | --- | --- | --- |
| MS-1 Auth | `auth.rpc.q` | RPC | Validacion token, roles, usuarios, token reset interno | Implementado |
| MS-2 Periodos/Materias | `periodos_materias.rpc.q` | RPC | Materias, NRC, periodo activo | Implementado |
| MS-3 Docentes-Alumnos | `docentes_alumnos.rpc.q` | RPC | Alumnos, docentes, inscripcion, materias por alumno | Implementado |
| MS-4 Calificaciones | `calificaciones.rpc.q` | RPC | Concentrado, promedio, estadisticas | Implementado |
| MS-5 Asistencias | `asistencias.rpc.q` | RPC | Asistencias por alumno/materia, estadisticas | Implementado |
| MS-6 Notificaciones | `notificaciones.events.q` | Eventos | Procesamiento asincrono de correos | Implementado |
| MS-6 Notificaciones DLQ | `notificaciones.events.dlq` | DLQ | Eventos fallidos | Implementado |
| MS-7 Reportes | Sin cola propia | Consumidor | Consume otros servicios por RabbitMQ con fallback gRPC | Implementado como consumidor |

## Routing keys RPC

### Auth

- `rpc.auth.validate_token`
- `rpc.auth.check_role`
- `rpc.auth.get_user_by_id`
- `rpc.auth.create_or_get_user_identity`
- `rpc.auth.create_password_reset_token`

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

MS-1, MS-3 y MS-4 publican eventos en `agm.events`. MS-6 Notificaciones los
consume desde `notificaciones.events.q`.

- `event.notificaciones.bienvenida_alumno`
- `event.notificaciones.bienvenida_docente`
- `event.notificaciones.baja_alumno`
- `event.notificaciones.cierre_materia`
- `event.notificaciones.reset_password`

Los flujos REST/gRPC de notificaciones siguen disponibles para compatibilidad y
fallback. Los eventos permiten desacoplar el envio de correos del flujo
principal de los servicios productores.

## Dead Letter Queue

La cola normal de eventos es `notificaciones.events.q`. Si MS-6 recibe un
evento invalido o el handler falla de forma definitiva, el consumer rechaza el
mensaje con `requeue=False`. RabbitMQ entonces lo enruta al Dead Letter
Exchange `agm.events.dlx`, que entrega el mensaje a `notificaciones.events.dlq`.

La DLQ guarda mensajes fallidos para revision. No reintenta automaticamente y
puede inspeccionarse o purgarse desde RabbitMQ UI.

Conceptos visibles en RabbitMQ UI:

- `D`: cola durable.
- `DLX`: Dead Letter Exchange configurado.
- `DLK`: Dead Letter Routing Key configurada.

## COMMUNICATION_MODE

| Valor | Comportamiento |
| --- | --- |
| `grpc` | Usa solo gRPC. |
| `rabbit` | Usa solo RabbitMQ. |
| `hybrid` | Usa RabbitMQ como principal y gRPC como fallback. |

`hybrid` es el modo recomendado. El fallback se activa ante errores de
transporte como timeout, broker detenido, conexion rechazada, canal cerrado o
errores equivalentes de RabbitMQ. No se usa para ocultar respuestas de negocio
validas como token invalido, materia no encontrada, alumno no inscrito, listas
vacias o eventos con payload invalido.

## RabbitMQ UI

- URL: `http://localhost:15673`
- Credenciales: `agm / agm_password`
- Puerto AMQP dentro de Docker: `5672`
- Puerto AMQP expuesto en host: `5673`

Verifica el estado efectivo con:

```bash
docker compose ps rabbitmq
```

## Comandos Docker

Levantar RabbitMQ:

```bash
docker compose up -d rabbitmq
```

Levantar servicios principales:

```bash
docker compose up -d rabbitmq ms-auth ms-periodos-materias ms-docentes-alumnos ms-calificaciones ms-asistencias ms-notificaciones ms-reportes
```

Ver logs:

```bash
docker compose logs --tail=100 ms-notificaciones
docker compose logs --tail=100 ms-reportes
docker compose logs --tail=100 rabbitmq
```

## Pruebas de integracion

Los comandos detallados estan en [PRUEBAS_RABBITMQ.md](PRUEBAS_RABBITMQ.md).

Scripts individuales:

```bash
docker compose exec -T ms-auth python scripts/test_auth_rabbit_rpc.py
docker compose exec -T ms-periodos-materias python scripts/test_periodos_rabbit_rpc.py
docker compose exec -T ms-docentes-alumnos python scripts/test_docentes_rabbit_rpc.py
docker compose exec -T ms-calificaciones python scripts/test_calificaciones_rabbit_rpc.py
docker compose exec -T ms-asistencias python scripts/test_asistencias_rabbit_rpc.py
docker compose exec -T ms-notificaciones python scripts/test_notification_events.py
docker compose exec -T ms-notificaciones python scripts/test_notification_dlq.py
```

Runner central:

```powershell
py -3 tests/integration/run_rabbitmq_checks.py
```

Topologia:

```powershell
py -3 tests/integration/check_rabbitmq_topology.py
```

En sistemas con Python en `PATH`, se puede usar `python` en lugar de `py -3`.

## Prueba de fallback gRPC

1. Levantar servicios.

```bash
docker compose up -d rabbitmq ms-auth ms-periodos-materias ms-docentes-alumnos ms-calificaciones ms-asistencias ms-notificaciones ms-reportes
```

2. Probar un flujo con RabbitMQ activo.

3. Apagar RabbitMQ:

```bash
docker compose stop rabbitmq
```

4. Repetir el flujo.

5. Verificar logs:

```text
RabbitMQ RPC failed, falling back to gRPC
RabbitMQ event publish failed, falling back to gRPC
```

6. Levantar RabbitMQ al final:

```bash
docker compose up -d rabbitmq
```

Flujos recomendados para validar fallback:

- `forgot-password`
- baja alumno
- creacion docente
- reportes/asistencias

## Pruebas funcionales relevantes validadas

- Auth RPC responde.
- Periodos RPC responde.
- Docentes-Alumnos RPC responde.
- Calificaciones RPC responde.
- Asistencias RPC responde.
- Reportes consume Calificaciones y Asistencias por RabbitMQ.
- Notificaciones procesa eventos.
- Notificaciones manda correos reales.
- Baja alumno usa correo real y materia real.
- Bienvenida alumno/docente incluye token inicial de reset password.
- DLQ recibe eventos invalidos.
- gRPC funciona como fallback.

## Estado final

Implementado:

- RabbitMQ en Docker.
- Infraestructura compartida de mensajeria.
- RPC RabbitMQ para Auth, Periodos, Docentes, Calificaciones y Asistencias.
- Clientes hibridos con fallback gRPC.
- Eventos RabbitMQ para Notificaciones.
- Productores reales de eventos.
- DLQ para eventos fallidos.
- Pruebas de integracion.
- Documentacion.

Pendiente o mejoras futuras:

- Automatizar mas pruebas end-to-end con datos controlados.
- Agregar monitoreo/alertas para DLQ.
- Reprocesamiento automatico/manual asistido de DLQ.
- Healthchecks avanzados de RabbitMQ por servicio.
- Optimizacion de conexiones si se requiere alto rendimiento.

## Decisiones tecnicas

- gRPC se mantuvo porque ya funcionaba y permite fallback ante fallos de
  RabbitMQ.
- RabbitMQ reduce acoplamiento directo entre servicios.
- El modo hibrido permite migracion gradual sin romper REST ni flujos
  existentes.
- Notificaciones por eventos desacopla el envio de correos del flujo principal.
- La DLQ evita reintentos infinitos y conserva eventos fallidos para analisis.

## Resumen para exposicion

AGM paso de una comunicacion directa entre microservicios por gRPC a una
arquitectura hibrida donde RabbitMQ funciona como middleware principal. Los
servicios primero intentan comunicarse por RabbitMQ y, si el broker falla, usan
gRPC como fallback. Ademas, Notificaciones procesa eventos asincronos y cuenta
con DLQ para manejar eventos invalidos sin bloquear el sistema.
