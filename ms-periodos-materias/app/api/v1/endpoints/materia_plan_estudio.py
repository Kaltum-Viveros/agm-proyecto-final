from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.responses import success_response
from app.db.session import get_db
from app.schemas.materia_plan_estudio import (
    MateriaPlanEstudioCreate,
    MateriaPlanEstudioRead,
    MateriaPlanEstudioUpdate,
)
from app.services.materia_plan_estudio_service import MateriaPlanEstudioService

router = APIRouter()


@router.get("")
async def list_materias_planes_estudio(
    materia_catalogo_id: UUID | None = Query(default=None),
    plan_estudio_id: UUID | None = Query(default=None),
    activa: bool | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    service = MateriaPlanEstudioService(db)
    relaciones = await service.list_relaciones(
        materia_catalogo_id=materia_catalogo_id,
        plan_estudio_id=plan_estudio_id,
        activa=activa,
    )

    return success_response(
        data=[
            MateriaPlanEstudioRead.model_validate(relacion).model_dump(mode="json")
            for relacion in relaciones
        ],
        message="Relaciones materia-plan de estudio obtenidas correctamente",
    )


@router.get("/{materia_plan_estudio_id}")
async def get_materia_plan_estudio(
    materia_plan_estudio_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    service = MateriaPlanEstudioService(db)
    relacion = await service.get_relacion(materia_plan_estudio_id)

    return success_response(
        data=MateriaPlanEstudioRead.model_validate(relacion).model_dump(mode="json"),
        message="Relación materia-plan de estudio obtenida correctamente",
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_materia_plan_estudio(
    payload: MateriaPlanEstudioCreate,
    db: AsyncSession = Depends(get_db),
):
    service = MateriaPlanEstudioService(db)
    relacion = await service.create_relacion(payload)

    return success_response(
        data=MateriaPlanEstudioRead.model_validate(relacion).model_dump(mode="json"),
        message="Relación materia-plan de estudio creada correctamente",
    )


@router.patch("/{materia_plan_estudio_id}")
async def update_materia_plan_estudio(
    materia_plan_estudio_id: UUID,
    payload: MateriaPlanEstudioUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = MateriaPlanEstudioService(db)
    relacion = await service.update_relacion(materia_plan_estudio_id, payload)

    return success_response(
        data=MateriaPlanEstudioRead.model_validate(relacion).model_dump(mode="json"),
        message="Relación materia-plan de estudio actualizada correctamente",
    )


@router.delete("/{materia_plan_estudio_id}")
async def deactivate_materia_plan_estudio(
    materia_plan_estudio_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    service = MateriaPlanEstudioService(db)
    relacion = await service.deactivate_relacion(materia_plan_estudio_id)

    return success_response(
        data=MateriaPlanEstudioRead.model_validate(relacion).model_dump(mode="json"),
        message="Relación materia-plan de estudio desactivada correctamente",
    )