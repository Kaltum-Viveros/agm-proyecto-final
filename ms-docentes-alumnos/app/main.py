from fastapi import FastAPI
from app.api.v1.endpoints import docentes
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version="1.0.0"
)

# Registramos las rutas de docentes
app.include_router(docentes.router, prefix="/api/v1/docentes", tags=["Docentes"])

@app.get("/")
def health_check():
    return {"status": "ok", "message": "MS Docentes y Alumnos funcionando"}