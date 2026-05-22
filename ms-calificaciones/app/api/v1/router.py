from fastapi import APIRouter, Depends
from app.api.deps import get_current_user

from app.api.v1.endpoints import (
    actividades,
    calificaciones,
    concentrado,
    health,
    ponderaciones,
)

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(ponderaciones.router, dependencies=[Depends(get_current_user)])
api_router.include_router(actividades.router, dependencies=[Depends(get_current_user)])
api_router.include_router(calificaciones.router, dependencies=[Depends(get_current_user)])
api_router.include_router(concentrado.router, dependencies=[Depends(get_current_user)])