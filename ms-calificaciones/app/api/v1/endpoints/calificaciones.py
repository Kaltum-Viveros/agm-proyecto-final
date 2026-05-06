from uuid import UUID

from fastapi import APIRouter, status

from app.core.responses import success_response
from app.repositories.actividad_memory_repository import ActividadMemoryRepository
from app.repositories.calificacion_memory_repository import CalificacionMemoryRepository
from app.schemas.calificacion import CalificacionCreate, CalificacionUpdate
from app.services.calificacion_service import CalificacionService

router = APIRouter(prefix="/calificaciones", tags=["Calificaciones"])

calificacion_repository = CalificacionMemoryRepository()
actividad_repository = ActividadMemoryRepository()

service = CalificacionService(
    calificacion_repository=calificacion_repository,
    actividad_repository=actividad_repository,
)


@router.post("", status_code=status.HTTP_201_CREATED)
def crear_calificacion(payload: CalificacionCreate):
    data = service.crear(payload)

    return success_response(
        data=data,
        message="Calificación registrada correctamente",
    )


@router.get("/actividad/{actividad_id}")
def obtener_calificaciones_por_actividad(actividad_id: UUID):
    data = service.obtener_por_actividad(actividad_id)

    return success_response(
        data=data,
        message="Calificaciones obtenidas correctamente",
    )


@router.get("/alumno/{alumno_id}/materia/{materia_id}")
def obtener_calificaciones_por_alumno_y_materia(alumno_id: UUID, materia_id: UUID):
    data = service.obtener_por_alumno_y_materia(
        alumno_id=alumno_id,
        materia_id=materia_id,
    )

    return success_response(
        data=data,
        message="Calificaciones del alumno obtenidas correctamente",
    )


@router.get("/{calificacion_id}")
def obtener_calificacion_por_id(calificacion_id: UUID):
    data = service.obtener_por_id(calificacion_id)

    return success_response(
        data=data,
        message="Calificación obtenida correctamente",
    )


@router.put("/{calificacion_id}")
def actualizar_calificacion(calificacion_id: UUID, payload: CalificacionUpdate):
    data = service.actualizar(calificacion_id, payload)

    return success_response(
        data=data,
        message="Calificación actualizada correctamente",
    )


@router.delete("/{calificacion_id}", status_code=status.HTTP_200_OK)
def eliminar_calificacion(calificacion_id: UUID):
    service.eliminar(calificacion_id)

    return success_response(
        data=None,
        message="Calificación eliminada correctamente",
    )