import sys
import os
import asyncio
import threading

# --- EL TRUCO PARA ARREGLAR gRPC EN PYTHON ---
# Obtenemos la ruta absoluta de la carpeta raíz del microservicio
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Añadimos la carpeta 'generated' al inicio del path para que los imports internos de gRPC funcionen
sys.path.insert(0, os.path.join(BASE_DIR, "app", "grpc", "generated"))
# ---------------------------------------------

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.base import Base
from app.db.session import engine
from app.models.docente import Docente
from app.models.alumno import Alumno
from app.models.inscripcion import Inscripcion 

# 1. IMPORTANTE: Importa el router centralizado que ya configuraste bien
from app.api.v1.router import api_router 
from app.messaging.rabbit_worker import start_rabbit_worker
from app.core.config import settings

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MS Docentes y Alumnos",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. ÚNICA LÍNEA DE REGISTRO:
# Aquí usamos el router central que unifica docentes y alumnos bajo "Importación"
app.include_router(api_router, prefix="/api/v1")


def _run_rabbit_worker():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_rabbit_worker())


@app.on_event("startup")
def start_background_workers():
    rabbit_thread = threading.Thread(target=_run_rabbit_worker, daemon=True)
    rabbit_thread.start()


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "MS Docentes y Alumnos funcionando"}
