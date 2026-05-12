from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.responses import success_response
from app.db.session import get_db
from app.schemas.materia_ofertada import (
    MateriaOfertadaCreate,
    MateriaOfertadaRead,
    MateriaOfertadaUpdate,
    MateriaOfertadaAsignarDocente,
)
from app.services.materia_ofertada_service import MateriaOfertadaService

router = APIRouter()


@router.get("")
async def list_materias_ofertadas(
    periodo_id: UUID | None = Query(default=None),
    materia_catalogo_id: UUID | None = Query(default=None),
    docente_id: UUID | None = Query(default=None),
    estado: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    service = MateriaOfertadaService(db)
    materias = await service.list_materias_ofertadas(
        periodo_id=periodo_id,
        materia_catalogo_id=materia_catalogo_id,
        docente_id=docente_id,
        estado=estado,
    )

    return success_response(
        data=[
            MateriaOfertadaRead.model_validate(materia).model_dump(mode="json")
            for materia in materias
        ],
        message="Materias ofertadas obtenidas correctamente",
    )


@router.get("/{materia_ofertada_id}")
async def get_materia_ofertada(
    materia_ofertada_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    service = MateriaOfertadaService(db)
    materia = await service.get_materia_ofertada(materia_ofertada_id)

    return success_response(
        data=MateriaOfertadaRead.model_validate(materia).model_dump(mode="json"),
        message="Materia ofertada obtenida correctamente",
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_materia_ofertada(
    payload: MateriaOfertadaCreate,
    db: AsyncSession = Depends(get_db),
):
    service = MateriaOfertadaService(db)
    materia = await service.create_materia_ofertada(payload)

    return success_response(
        data=MateriaOfertadaRead.model_validate(materia).model_dump(mode="json"),
        message="Materia ofertada creada correctamente",
    )


@router.patch("/{materia_ofertada_id}")
async def update_materia_ofertada(
    materia_ofertada_id: UUID,
    payload: MateriaOfertadaUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = MateriaOfertadaService(db)
    materia = await service.update_materia_ofertada(materia_ofertada_id, payload)

    return success_response(
        data=MateriaOfertadaRead.model_validate(materia).model_dump(mode="json"),
        message="Materia ofertada actualizada correctamente",
    )


@router.delete("/{materia_ofertada_id}")
async def deactivate_materia_ofertada(
    materia_ofertada_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    service = MateriaOfertadaService(db)
    materia = await service.deactivate_materia_ofertada(materia_ofertada_id)

    return success_response(
        data=MateriaOfertadaRead.model_validate(materia).model_dump(mode="json"),
        message="Materia ofertada desactivada correctamente",
    )

@router.patch("/{materia_ofertada_id}/activar")
async def activar_materia_ofertada(
    materia_ofertada_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    service = MateriaOfertadaService(db)
    materia = await service.activar_materia_ofertada(materia_ofertada_id)

    return success_response(
        data=MateriaOfertadaRead.model_validate(materia).model_dump(mode="json"),
        message="Materia ofertada activada correctamente",
    )


@router.patch("/{materia_ofertada_id}/cerrar")
async def cerrar_materia_ofertada(
    materia_ofertada_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    service = MateriaOfertadaService(db)
    materia = await service.cerrar_materia_ofertada(materia_ofertada_id)

    return success_response(
        data=MateriaOfertadaRead.model_validate(materia).model_dump(mode="json"),
        message="Materia ofertada cerrada correctamente",
    )


@router.patch("/{materia_ofertada_id}/cancelar")
async def cancelar_materia_ofertada(
    materia_ofertada_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    service = MateriaOfertadaService(db)
    materia = await service.cancelar_materia_ofertada(materia_ofertada_id)

    return success_response(
        data=MateriaOfertadaRead.model_validate(materia).model_dump(mode="json"),
        message="Materia ofertada cancelada correctamente",
    )


@router.patch("/{materia_ofertada_id}/asignar-docente")
async def asignar_docente_materia_ofertada(
    materia_ofertada_id: UUID,
    payload: MateriaOfertadaAsignarDocente,
    db: AsyncSession = Depends(get_db),
):
    service = MateriaOfertadaService(db)
    materia = await service.asignar_docente_materia_ofertada(
        materia_ofertada_id=materia_ofertada_id,
        docente_id=payload.docente_id,
        docente_nombre=payload.docente_nombre,
    )

    return success_response(
        data=MateriaOfertadaRead.model_validate(materia).model_dump(mode="json"),
        message="Docente asignado correctamente a la materia ofertada",
    )