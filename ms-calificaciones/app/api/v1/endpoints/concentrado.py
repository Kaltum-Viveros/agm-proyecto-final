from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.core.responses import success_response
from app.dependencies import get_concentrado_service
from app.services.concentrado_service import ConcentradoService

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