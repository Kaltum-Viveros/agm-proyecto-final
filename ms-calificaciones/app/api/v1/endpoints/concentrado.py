from uuid import UUID

from fastapi import APIRouter

from app.core.responses import success_response
from app.repositories.actividad_memory_repository import ActividadMemoryRepository
from app.repositories.calificacion_memory_repository import CalificacionMemoryRepository
from app.repositories.ponderacion_memory_repository import PonderacionMemoryRepository
from app.services.concentrado_service import ConcentradoService

router = APIRouter(prefix="/concentrado", tags=["Concentrado"])

ponderacion_repository = PonderacionMemoryRepository()
actividad_repository = ActividadMemoryRepository()
calificacion_repository = CalificacionMemoryRepository()

service = ConcentradoService(
    ponderacion_repository=ponderacion_repository,
    actividad_repository=actividad_repository,
    calificacion_repository=calificacion_repository,
)


@router.get("/{materia_id}")
def obtener_concentrado(materia_id: UUID):
    data = service.obtener_concentrado(materia_id)

    return success_response(
        data=data,
        message="Concentrado obtenido correctamente",
    )