from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile, status

from app.core.responses import success_response
from app.dependencies import (
    get_calificacion_service,
    get_importacion_calificaciones_service,
)
from app.schemas.calificacion import CalificacionCreate, CalificacionUpdate
from app.services.calificacion_service import CalificacionService
from app.services.importacion_calificaciones_service import ImportacionCalificacionesService

router = APIRouter(prefix="/calificaciones", tags=["Calificaciones"])


@router.post("", status_code=status.HTTP_201_CREATED)
def crear_calificacion(
    payload: CalificacionCreate,
    service: CalificacionService = Depends(get_calificacion_service),
):
    data = service.crear(payload)

    return success_response(
        data=data,
        message="Calificación registrada correctamente",
    )


@router.post("/importar", status_code=status.HTTP_201_CREATED)
async def importar_calificaciones(
    actividad_id: UUID = Form(...),
    archivo: UploadFile = File(...),
    service: ImportacionCalificacionesService = Depends(
        get_importacion_calificaciones_service
    ),
):
    data = await service.importar_excel(
        actividad_id=actividad_id,
        archivo=archivo,
    )

    return success_response(
        data=data,
        message="Importación de calificaciones finalizada",
    )


@router.get("/actividad/{actividad_id}")
def obtener_calificaciones_por_actividad(
    actividad_id: UUID,
    service: CalificacionService = Depends(get_calificacion_service),
):
    data = service.obtener_por_actividad(actividad_id)

    return success_response(
        data=data,
        message="Calificaciones obtenidas correctamente",
    )


@router.get("/alumno/{alumno_id}/materia/{materia_id}")
def obtener_calificaciones_por_alumno_y_materia(
    alumno_id: UUID,
    materia_id: UUID,
    service: CalificacionService = Depends(get_calificacion_service),
):
    data = service.obtener_por_alumno_y_materia(
        alumno_id=alumno_id,
        materia_id=materia_id,
    )

    return success_response(
        data=data,
        message="Calificaciones del alumno obtenidas correctamente",
    )


@router.get("/{calificacion_id}")
def obtener_calificacion_por_id(
    calificacion_id: UUID,
    service: CalificacionService = Depends(get_calificacion_service),
):
    data = service.obtener_por_id(calificacion_id)

    return success_response(
        data=data,
        message="Calificación obtenida correctamente",
    )


@router.put("/{calificacion_id}")
def actualizar_calificacion(
    calificacion_id: UUID,
    payload: CalificacionUpdate,
    service: CalificacionService = Depends(get_calificacion_service),
):
    data = service.actualizar(calificacion_id, payload)

    return success_response(
        data=data,
        message="Calificación actualizada correctamente",
    )


@router.delete("/{calificacion_id}", status_code=status.HTTP_200_OK)
def eliminar_calificacion(
    calificacion_id: UUID,
    service: CalificacionService = Depends(get_calificacion_service),
):
    service.eliminar(calificacion_id)

    return success_response(
        data=None,
        message="Calificación eliminada correctamente",
    )