from fastapi import APIRouter

from app.api.v1.endpoints import (
    health, 
    materias_catalogo, 
    periodos, 
    planes_estudio, 
    materias_ofertadas, 
    materia_plan_estudio, 
    materia_horarios
)

api_router = APIRouter()

# ruta del endpoint de salud 
api_router.include_router(health.router)

# ruta de los endpoints de periodos, planes de estudio y materias del catálogo
api_router.include_router(
    periodos.router, 
    prefix="/periodos", 
    tags=["Periodos"]
)

api_router.include_router(
    planes_estudio.router,
    prefix="/planes-estudio",
    tags=["Planes de estudio"],
)

api_router.include_router(
    materias_catalogo.router,
    prefix="/materias-catalogo",
    tags=["Materias catálogo"],
)

# rutas de los endpoints de materias ofertadas, materias por plan de estudio y horarios de materia
api_router.include_router(
    materia_plan_estudio.router,
    prefix="/materias-planes-estudio",
    tags=["Materias - Planes de estudio"],
)

api_router.include_router(
    materias_ofertadas.router,
    prefix="/materias-ofertadas",
    tags=["Materias ofertadas"],
)

api_router.include_router(
    materia_horarios.router,
    prefix="/materia-horarios",
    tags=["Horarios de materia"],
)