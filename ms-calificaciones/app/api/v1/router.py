from fastapi import APIRouter, Depends
from app.dependencies import verificar_token_simulado

from app.api.v1.endpoints import (
    actividades,
    calificaciones,
    concentrado,
    health,
    ponderaciones,
)

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(ponderaciones.router, dependencies=[Depends(verificar_token_simulado)])
api_router.include_router(actividades.router, dependencies=[Depends(verificar_token_simulado)])
api_router.include_router(calificaciones.router, dependencies=[Depends(verificar_token_simulado)])
api_router.include_router(concentrado.router, dependencies=[Depends(verificar_token_simulado)])