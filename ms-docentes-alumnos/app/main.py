import sys
import os

# --- EL TRUCO PARA ARREGLAR gRPC EN PYTHON ---
# Obtenemos la ruta absoluta de la carpeta raíz del microservicio
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Añadimos la carpeta 'generated' al inicio del path para que los imports internos de gRPC funcionen
sys.path.insert(0, os.path.join(BASE_DIR, "app", "grpc", "generated"))
# ---------------------------------------------

from fastapi import FastAPI
from app.db.base import Base
from app.db.session import engine
from app.models.docente import Docente
from app.models.alumno import Alumno
from app.models.inscripcion import Inscripcion 

# 1. IMPORTANTE: Importa el router centralizado que ya configuraste bien
from app.api.v1.router import api_router 

Base.metadata.create_all(bind=engine)

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="MS Docentes y Alumnos",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://localhost:3000", "http://localhost:5173", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. ÚNICA LÍNEA DE REGISTRO:
# Aquí usamos el router central que unifica docentes y alumnos bajo "Importación"
app.include_router(api_router, prefix="/api/v1")

@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "MS Docentes y Alumnos funcionando"}