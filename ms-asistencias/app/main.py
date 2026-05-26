import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import rutas_asistencias, rutas_qr, rutas_sesiones
from app.core.config import settings
from app.messaging.rabbit_worker import start_rabbit_worker


@asynccontextmanager
async def lifespan(app: FastAPI):
    rabbit_task = asyncio.create_task(start_rabbit_worker())
    try:
        yield
    finally:
        rabbit_task.cancel()
        await asyncio.gather(rabbit_task, return_exceptions=True)


app = FastAPI(
    title="MS-5: Asistencias QR",
    description="Microservicio para la gestion de pases de lista mediante codigos QR dinamicos.",
    version="1.0.0",
    lifespan=lifespan,
)

# Configuracion de CORS
origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]

if settings.ENVIRONMENT == "production" and "*" in origins:
    logging.warning("CORS configurado con '*' en ambiente de produccion. Esto es un riesgo de seguridad.")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro de Rutas
app.include_router(rutas_sesiones.router)
app.include_router(rutas_qr.router)
app.include_router(rutas_asistencias.router)


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Endpoint basico para comprobar que el microservicio esta vivo.
    """
    return {"status": "ok", "service": "ms-asistencias"}
