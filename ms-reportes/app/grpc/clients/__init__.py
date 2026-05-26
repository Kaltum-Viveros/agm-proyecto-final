import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent / "generated"))

from app.messaging.clients.periodos_hybrid_client import periodos_materias_client
from app.messaging.clients.calificaciones_hybrid_client import calificaciones_client
from .docentes_alumnos_client import docentes_alumnos_client


class _LazyAsistenciasClient:
    def __getattr__(self, name):
        from app.messaging.clients.asistencias_hybrid_client import asistencias_client

        return getattr(asistencias_client, name)


asistencias_client = _LazyAsistenciasClient()

__all__ = [
    "periodos_materias_client",
    "docentes_alumnos_client",
    "calificaciones_client",
    "asistencias_client",
]
