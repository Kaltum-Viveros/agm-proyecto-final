from fastapi import APIRouter
from app.api.v1.endpoints import alumnos, docentes, inscripciones, importar, importar_alumnos

api_router = APIRouter()

# Registro de módulos individuales
api_router.include_router(alumnos.router, prefix="/alumnos", tags=["Alumnos"])
api_router.include_router(docentes.router, prefix="/docentes", tags=["Docentes"])
api_router.include_router(inscripciones.router, prefix="/inscripciones", tags=["Inscripciones"])

# Unificación de la sección de Importación
# Ambos routers se montan bajo el mismo prefijo y el mismo tag para Swagger
api_router.include_router(importar.router, prefix="/importar", tags=["Importación"])
api_router.include_router(importar_alumnos.router, prefix="/importar", tags=["Importación"])