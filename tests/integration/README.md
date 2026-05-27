# Pruebas de integracion RabbitMQ

Estas pruebas centralizan los scripts manuales de RabbitMQ existentes en los
microservicios AGM. No modifican endpoints REST, `.proto`, modelos ni reglas de
negocio.

## Requisitos

- Docker Compose disponible desde el host.
- Servicios construidos y levantados con RabbitMQ:

```powershell
docker compose up -d rabbitmq ms-auth ms-periodos-materias ms-docentes-alumnos ms-calificaciones ms-asistencias ms-notificaciones
```

## Ejecutar pruebas RPC y eventos

```powershell
python tests/integration/run_rabbitmq_checks.py
```

Valida:

- Auth RPC: `ms-auth/scripts/test_auth_rabbit_rpc.py`
- Periodos/Materias RPC: `ms-periodos-materias/scripts/test_periodos_rabbit_rpc.py`
- Docentes-Alumnos RPC: `ms-docentes-alumnos/scripts/test_docentes_rabbit_rpc.py`
- Calificaciones RPC: `ms-calificaciones/scripts/test_calificaciones_rabbit_rpc.py`
- Asistencias RPC: `ms-asistencias/scripts/test_asistencias_rabbit_rpc.py`
- Eventos de Notificaciones: `ms-notificaciones/scripts/test_notification_events.py`
- DLQ de Notificaciones: `ms-notificaciones/scripts/test_notification_dlq.py`

El runner se detiene en el primer fallo y deja visible stdout/stderr del script
fallido.

## Validar topologia RabbitMQ

```powershell
python tests/integration/check_rabbitmq_topology.py
```

Usa la API HTTP de RabbitMQ Management en `http://localhost:15673` con las
credenciales `agm / agm_password`.

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

## Efectos esperados

- Las pruebas RPC usan UUIDs o valores inexistentes controlados.
- La prueba de eventos publica un evento `reset_password` de prueba y puede
  generar un registro de notificacion/correo de prueba.
- La prueba DLQ publica un evento invalido de baja de alumno para confirmar que
  termina en `notificaciones.events.dlq`.
- No se crean alumnos/docentes reales ni se ejecutan bajas reales desde el
  runner central.
