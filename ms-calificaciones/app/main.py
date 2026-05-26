from contextlib import asynccontextmanager
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.grpc.server import start_grpc_server, stop_grpc_server
from app.messaging.rabbit_worker import start_rabbit_worker

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Iniciar servidor gRPC en segundo plano
    await start_grpc_server()
    rabbit_task = asyncio.create_task(start_rabbit_worker())
    try:
        yield
    finally:
        rabbit_task.cancel()
        await stop_grpc_server()


from app.api.v1.router import api_router
from app.core.config import settings

app = FastAPI(
    title="AGM - MS Calificaciones & Ponderaciones",
    version="0.1.0",
    description="Microservicio de ponderaciones, actividades, calificaciones y concentrados.",
    lifespan=lifespan
)

import logging

# Advertencia de seguridad en producción
if settings.env == "production" and "*" in settings.cors_origins_list:
    logging.warning("⚠️ CORS configurado con '*' en ambiente de producción. Esto es un riesgo de seguridad.")

# Configuración de CORS para el Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root():
    return {
        "success": True,
        "service": settings.service_name,
        "message": "MS Calificaciones & Ponderaciones",
    }
