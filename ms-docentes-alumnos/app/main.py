from fastapi import FastAPI
# --- IMPORTACIONES PARA BASE DE DATOS ---
from app.db.base import Base        # 1. Traemos la Base limpia
from app.db.session import engine   # 2. El motor de conexión
from app.models.docente import Docente # 3. Importamos modelos para que Base los registre
from app.models.alumno import Alumno
# ----------------------------------------

from app.api.v1.endpoints import alumnos, docentes, inscripciones, importar

# Crear las tablas físicamente en PostgreSQL al iniciar
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MS Docentes y Alumnos",
    version="1.0.0"
)

# Registramos los routers
app.include_router(alumnos.router, prefix="/api/v1/alumnos", tags=["Alumnos"])
app.include_router(docentes.router, prefix="/api/v1/docentes", tags=["Docentes"])
app.include_router(inscripciones.router, prefix="/api/v1/inscripciones", tags=["Inscripciones"])
app.include_router(importar.router, prefix="/api/v1/importar", tags=["Importación"])

@app.get("/")
def health_check():
    return {"status": "ok", "message": "MS Docentes y Alumnos funcionando"}