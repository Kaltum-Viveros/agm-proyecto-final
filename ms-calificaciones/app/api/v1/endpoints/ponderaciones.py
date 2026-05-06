from uuid import UUID

from fastapi import APIRouter, status

from app.core.responses import success_response
from app.repositories.ponderacion_memory_repository import PonderacionMemoryRepository
from app.schemas.ponderacion import PonderacionesCreate
from app.services.ponderacion_service import PonderacionService

router = APIRouter(prefix="/ponderaciones", tags=["Ponderaciones"])

repository = PonderacionMemoryRepository()
service = PonderacionService(repository)


@router.post("/{materia_id}", status_code=status.HTTP_201_CREATED)
def crear_ponderaciones(materia_id: UUID, payload: PonderacionesCreate):
    data = service.crear_o_reemplazar(materia_id, payload)
    return success_response(
        data=data,
        message="Ponderaciones configuradas correctamente",
    )


@router.get("/{materia_id}")
def obtener_ponderaciones(materia_id: UUID):
    data = service.obtener_por_materia(materia_id)
    return success_response(
        data=data,
        message="Ponderaciones obtenidas correctamente",
    )


@router.put("/{materia_id}")
def actualizar_ponderaciones(materia_id: UUID, payload: PonderacionesCreate):
    data = service.crear_o_reemplazar(materia_id, payload)
    return success_response(
        data=data,
        message="Ponderaciones actualizadas correctamente",
    )