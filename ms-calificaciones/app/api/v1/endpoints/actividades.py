from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.core.responses import success_response
from app.dependencies import get_actividad_service
from app.schemas.actividad import ActividadCreate, ActividadUpdate
from app.services.actividad_service import ActividadService
from app.api.deps import role_required

router = APIRouter(prefix="/actividades", tags=["Actividades"])


@router.post("", status_code=status.HTTP_201_CREATED)
def crear_actividad(
    payload: ActividadCreate,
    service: ActividadService = Depends(get_actividad_service),
    _user = Depends(role_required("DOCENTE")),
):
    data = service.crear(payload)

    return success_response(
        data=data,
        message="Actividad creada correctamente",
    )


@router.get("/materia/{materia_id}")
def obtener_actividades_por_materia(
    materia_id: UUID,
    service: ActividadService = Depends(get_actividad_service),
):
    data = service.obtener_por_materia(materia_id)

    return success_response(
        data=data,
        message="Actividades obtenidas correctamente",
    )


@router.get("/{actividad_id}")
def obtener_actividad_por_id(
    actividad_id: UUID,
    service: ActividadService = Depends(get_actividad_service),
):
    data = service.obtener_por_id(actividad_id)

    return success_response(
        data=data,
        message="Actividad obtenida correctamente",
    )


@router.put("/{actividad_id}")
def actualizar_actividad(
    actividad_id: UUID,
    payload: ActividadUpdate,
    service: ActividadService = Depends(get_actividad_service),
    _user = Depends(role_required("DOCENTE")),
):
    data = service.actualizar(actividad_id, payload)

    return success_response(
        data=data,
        message="Actividad actualizada correctamente",
    )


@router.delete("/{actividad_id}", status_code=status.HTTP_200_OK)
def eliminar_actividad(
    actividad_id: UUID,
    service: ActividadService = Depends(get_actividad_service),
    _user = Depends(role_required("DOCENTE")),
):
    service.eliminar(actividad_id)

    return success_response(
        data=None,
        message="Actividad eliminada correctamente",
    )