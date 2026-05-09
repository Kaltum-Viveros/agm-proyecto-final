from fastapi import FastAPI
from app.api.v1.endpoints import docentes
from app.api.v1.endpoints import alumnos 
from app.api.v1.endpoints import inscripciones 
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version="1.0.0"
)

# Registramos las rutas de alumnos
app.include_router(alumnos.router, prefix="/api/v1/alumnos", tags=["Alumnos"])

# Registramos las rutas de docentes
app.include_router(docentes.router, prefix="/api/v1/docentes", tags=["Docentes"])

# Registramos las rutas de inscripciones
app.include_router(inscripciones.router, prefix="/api/v1/inscripciones", tags=["Inscripciones"])

@app.get("/")
def health_check():
    return {"status": "ok", "message": "MS Docentes y Alumnos funcionando"}
