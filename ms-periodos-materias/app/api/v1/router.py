from fastapi import APIRouter

from app.api.v1.endpoints import health, materias_catalogo, periodos, planes_estudio

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