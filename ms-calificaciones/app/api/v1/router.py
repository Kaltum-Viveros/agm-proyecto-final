from fastapi import APIRouter

from app.api.v1.endpoints import actividades, health, ponderaciones

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(ponderaciones.router)
api_router.include_router(actividades.router)