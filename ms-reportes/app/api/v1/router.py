from fastapi import APIRouter
from app.api.v1.endpoints import health, reportes, estadisticas

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(reportes.router, prefix="/reportes", tags=["Reportes"])
api_router.include_router(estadisticas.router, prefix="/estadisticas", tags=["Estadisticas"])
