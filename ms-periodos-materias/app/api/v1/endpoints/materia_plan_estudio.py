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
from app.core.pagination import build_paginated_response

router = APIRouter()


@router.get("")
async def list_materias_planes_estudio(
    plan_estudio_id: UUID | None = Query(default=None),
    materia_catalogo_id: UUID | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    service = MateriaPlanEstudioService(db)
    relaciones, total = await service.list_materias_planes_estudio(
        plan_estudio_id=plan_estudio_id,
        materia_catalogo_id=materia_catalogo_id,
        page=page,
        limit=limit,
    )

    items = [
        MateriaPlanEstudioRead.model_validate(relacion).model_dump(mode="json")
        for relacion in relaciones
    ]

    return success_response(
        data=build_paginated_response(
            items=items,
            total=total,
            page=page,
            limit=limit,
        ),
        message="Relaciones materia-plan obtenidas correctamente",
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