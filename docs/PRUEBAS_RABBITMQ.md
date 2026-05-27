# Pruebas RabbitMQ

Este documento resume como validar la mensajeria RabbitMQ del proyecto AGM. Las
pruebas estan pensadas para ejecutarse con Docker Compose y no modifican
endpoints REST, `.proto`, modelos ni reglas de negocio.

## Requisitos

Levantar los servicios principales:

```bash
docker compose up -d rabbitmq ms-auth ms-periodos-materias ms-docentes-alumnos ms-calificaciones ms-asistencias ms-notificaciones ms-reportes
```

RabbitMQ Management UI:

- URL: `http://localhost:15673`
- Credenciales: `agm / agm_password`

## Scripts individuales

RPC:

```bash
docker compose exec -T ms-auth python scripts/test_auth_rabbit_rpc.py
docker compose exec -T ms-periodos-materias python scripts/test_periodos_rabbit_rpc.py
docker compose exec -T ms-docentes-alumnos python scripts/test_docentes_rabbit_rpc.py
docker compose exec -T ms-calificaciones python scripts/test_calificaciones_rabbit_rpc.py
docker compose exec -T ms-asistencias python scripts/test_asistencias_rabbit_rpc.py
```

Eventos y DLQ:

```bash
docker compose exec -T ms-notificaciones python scripts/test_notification_events.py
docker compose exec -T ms-notificaciones python scripts/test_notification_dlq.py
```

## Runner central

Ejecuta todos los scripts anteriores en orden y se detiene ante el primer
fallo:

```powershell
py -3 tests/integration/run_rabbitmq_checks.py
```

Salida esperada:

```text
[OK] Auth RPC
[OK] Periodos RPC
[OK] Docentes-Alumnos RPC
[OK] Calificaciones RPC
[OK] Asistencias RPC
[OK] Notificaciones eventos
[OK] Notificaciones DLQ
```

En sistemas con Python en `PATH`, se puede usar:

```bash
python tests/integration/run_rabbitmq_checks.py
```

## Validacion de topologia

El script usa la API HTTP de RabbitMQ Management:

```powershell
py -3 tests/integration/check_rabbitmq_topology.py
```

Verifica colas:

- `auth.rpc.q`
- `periodos_materias.rpc.q`
- `docentes_alumnos.rpc.q`
- `calificaciones.rpc.q`
- `asistencias.rpc.q`
- `notificaciones.events.q`
- `notificaciones.events.dlq`

Verifica exchanges:

- `agm.rpc`
- `agm.events`
- `agm.events.dlx`

## Prueba DLQ

El script `test_notification_dlq.py` publica un evento invalido:

```text
event.notificaciones.baja_alumno
```

Payload:

```json
{
  "alumno_id": "",
  "materia_id": ""
}
```

Resultado esperado:

- MS-6 recibe el evento.
- El handler falla de forma controlada.
- El mensaje no se reintenta infinitamente.
- El mensaje queda en `notificaciones.events.dlq`.

## Prueba manual de fallback gRPC

El fallback apaga RabbitMQ y afecta a todo el entorno, por eso se documenta como
validacion manual.

1. Levantar servicios:

```bash
docker compose up -d rabbitmq ms-auth ms-periodos-materias ms-docentes-alumnos ms-calificaciones ms-asistencias ms-notificaciones ms-reportes
```

2. Probar un flujo con RabbitMQ activo.

3. Apagar RabbitMQ:

```bash
docker compose stop rabbitmq
```

4. Repetir el flujo.

5. Revisar logs:

```bash
docker compose logs --tail=100 ms-auth
docker compose logs --tail=100 ms-docentes-alumnos
docker compose logs --tail=100 ms-calificaciones
docker compose logs --tail=100 ms-reportes
```

Mensajes esperados:

```text
RabbitMQ RPC failed, falling back to gRPC
RabbitMQ event publish failed, falling back to gRPC
```

6. Volver a levantar RabbitMQ:

```bash
docker compose up -d rabbitmq
```

## Flujos funcionales relevantes

Se validan o pueden validarse con datos controlados:

- `forgot-password`: Auth publica evento `reset_password` y usa fallback gRPC
  si RabbitMQ falla.
- Creacion alumno: MS-3 publica `bienvenida_alumno`.
- Creacion docente: MS-3 publica `bienvenida_docente`.
- Baja alumno: MS-3 publica `baja_alumno`; MS-6 usa alumno real y materia real.
- Cierre materia: MS-4 publica `cierre_materia`.
- Reportes: MS-7 consume Calificaciones y Asistencias por RabbitMQ con fallback
  gRPC.

## Efectos de las pruebas

- Los scripts RPC usan UUIDs o valores inexistentes controlados.
- `test_notification_events.py` publica un reset password de prueba y puede
  generar registro/correo de prueba.
- `test_notification_dlq.py` deja un mensaje invalido en la DLQ.
- El runner central no crea alumnos/docentes reales ni ejecuta bajas reales.
