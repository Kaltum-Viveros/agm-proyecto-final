from fastapi import APIRouter

from app.core.config import get_settings
from app.core.responses import success_response

router = APIRouter(tags=["Health"])


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