from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import rutas_asistencias, rutas_qr, rutas_sesiones
from app.core.config import settings

app = FastAPI(
    title="MS-5: Asistencias QR",
    description="Microservicio para la gestión de pases de lista mediante códigos QR dinámicos.",
    version="1.0.0",
)

# Configuración de CORS
import logging
origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]

if settings.ENVIRONMENT == "production" and "*" in origins:
    logging.warning("⚠️ CORS configurado con '*' en ambiente de producción. Esto es un riesgo de seguridad.")
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
    Endpoint básico para comprobar que el microservicio está vivo.
    """
    return {"status": "ok", "service": "ms-asistencias"}
