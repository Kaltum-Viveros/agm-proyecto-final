from fastapi import APIRouter

from app.core.config import settings
from app.core.responses import success_response

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
def health_check():
    return success_response(
        data={
            "service": settings.service_name,
            "status": "ok",
            "database": "not_configured_yet",
        },
        message="Service is running",
    )