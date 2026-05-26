import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent / "generated"))

from app.messaging.clients.periodos_hybrid_client import periodos_materias_client
from .docentes_alumnos_client import docentes_alumnos_client
from .calificaciones_client import calificaciones_client
from .asistencias_client import asistencias_client

__all__ = [
    "periodos_materias_client",
    "docentes_alumnos_client",
    "calificaciones_client",
    "asistencias_client",
]
