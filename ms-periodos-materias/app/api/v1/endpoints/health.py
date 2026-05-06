from fastapi import APIRouter

from app.core.config import get_settings
from app.core.responses import success_response
from app.db.session import check_database_connection


router = APIRouter(tags=["Health"])

# Endpoint para verificar el estado general del microservicio
@router.get("/health")
async def health_check():
    settings = get_settings()

    return success_response(
        data={
            "service": settings.service_name,
            "environment": settings.environment,
            "status": "running",
        },
        message="MS-2 Periodos & Materias funcionando correctamente",
    )

# Endpoint para verificar la conexión a la base de datos
@router.get("/health/db")
async def database_health_check():
    is_connected = await check_database_connection()

    return success_response(
        data={
            "database": "connected" if is_connected else "disconnected",
        },
        message="Verificación de conexión a base de datos finalizada",
    )