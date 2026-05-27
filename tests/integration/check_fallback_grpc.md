# Validacion manual de fallback gRPC

El fallback gRPC apaga RabbitMQ y afecta a todos los microservicios, por eso no
se automatiza dentro de `run_rabbitmq_checks.py`.

## Pasos

1. Levantar servicios:

```powershell
docker compose up -d rabbitmq ms-auth ms-periodos-materias ms-docentes-alumnos ms-calificaciones ms-asistencias ms-notificaciones ms-reportes
```

2. Ejecutar un flujo normal, por ejemplo `forgot-password`.

3. Apagar RabbitMQ:

```powershell
docker compose stop rabbitmq
```

4. Repetir el mismo flujo.

5. Revisar logs del productor:

```powershell
docker compose logs --tail=100 ms-auth
docker compose logs --tail=100 ms-docentes-alumnos
docker compose logs --tail=100 ms-calificaciones
```

Debe aparecer un log similar a:

```text
RabbitMQ event publish failed, falling back to gRPC
RabbitMQ RPC failed, falling back to gRPC
```

6. Volver a levantar RabbitMQ:

```powershell
docker compose up -d rabbitmq
```

## Criterio de exito

- El endpoint probado no responde 500 por RabbitMQ apagado.
- El log muestra fallback gRPC.
- RabbitMQ queda levantado al final.
