from fastapi import FastAPI
from app.db.base import Base
from app.db.session import engine
from app.models.docente import Docente
from app.models.alumno import Alumno
from app.models.inscripcion import Inscripcion 

# 1. IMPORTANTE: Importa el router centralizado que ya configuraste bien
from app.api.v1.router import api_router 

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MS Docentes y Alumnos",
    version="1.0.0"
)

# 2. ÚNICA LÍNEA DE REGISTRO:
# Aquí usamos el router central que unifica docentes y alumnos bajo "Importación"
app.include_router(api_router, prefix="/api/v1")

@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "MS Docentes y Alumnos funcionando"}