from fastapi import APIRouter
from app.api.v1.endpoints import health, reportes

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(reportes.router, prefix="/reportes", tags=["Reportes"])
