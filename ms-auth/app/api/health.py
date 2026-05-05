from fastapi import APIRouter

from app.core.responses import success_response

router = APIRouter()


@router.get("/health")
def health_check() -> dict:
    return success_response(
        data={
            "service": "ms-auth",
            "status": "ok",
        },
        message="MS Auth funcionando correctamente",
    )