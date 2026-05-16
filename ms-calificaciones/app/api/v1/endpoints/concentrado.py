from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.core.responses import success_response
from app.dependencies import get_concentrado_service
from app.services.concentrado_service import ConcentradoService
from app.grpc.clients.notif_client import notif_client
from app.api.deps import role_required

router = APIRouter(prefix="/concentrado", tags=["Concentrado"])


@router.get("/{materia_id}")
def obtener_concentrado(
    materia_id: UUID,
    modo: Literal["actual", "final"] = Query(
        default="actual",
        description="actual = solo ponderaciones con calificaciones; final = faltantes cuentan como 0",
    ),
    service: ConcentradoService = Depends(get_concentrado_service),
):
    data = service.obtener_concentrado(materia_id=materia_id, modo=modo)

    return success_response(
        data=data,
        message="Concentrado obtenido correctamente",
    )


@router.post("/{materia_id}/cierre")
def cerrar_materia(
    materia_id: UUID,
    _user = Depends(role_required("DOCENTE")),
):
    """
    Cierra las actas de una materia y notifica a todos los alumnos por correo
    mediante el MS-6 (Notificaciones).
    """
    # 1. Enviar notificación masiva vía gRPC (MS-6)
    exito = notif_client.enviar_cierre_materia(materia_id=str(materia_id))
    
    if not exito:
        return success_response(
            data={"materia_id": materia_id, "notificados": False},
            message="Actas cerradas, pero hubo un problema al notificar a los alumnos (MS-6 no disponible o falló)."
        )

    return success_response(
        data={"materia_id": materia_id, "notificados": True},
        message="Materia cerrada exitosamente. Todos los alumnos han sido notificados."
    )