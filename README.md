# AGM Backend

AGM es una plataforma de gestion escolar basada en microservicios. El backend
expone APIs REST para frontend/Postman y usa comunicacion interna entre
microservicios.

La arquitectura interna actual usa RabbitMQ como canal principal y conserva
gRPC como fallback para mantener compatibilidad durante la migracion gradual.

## Documentacion

- [Arquitectura RabbitMQ y fallback gRPC](docs/ARQUITECTURA_RABBITMQ.md)

## Ejecucion rapida

```bash
docker compose up -d
```

RabbitMQ Management UI:

- URL: `http://localhost:15673`
- Credenciales: `agm / agm_password`

Si el entorno local usa los valores por defecto de `.env.example`, el puerto de
management puede estar publicado como `15672`. Verifica el puerto efectivo con:

```bash
docker compose ps rabbitmq
```
