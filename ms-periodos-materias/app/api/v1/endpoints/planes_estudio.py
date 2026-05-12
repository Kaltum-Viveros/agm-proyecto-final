from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.responses import success_response
from app.db.session import get_db
from app.schemas.plan_estudio import PlanEstudioCreate, PlanEstudioRead, PlanEstudioUpdate
from app.services.plan_estudio_service import PlanEstudioService
from app.core.pagination import build_paginated_response

router = APIRouter()


@router.get("")
async def list_planes_estudio(
    activo: bool | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    service = PlanEstudioService(db)
    planes, total = await service.list_planes_estudio(
        activo=activo,
        page=page,
        limit=limit,
    )

    items = [
        PlanEstudioRead.model_validate(plan).model_dump(mode="json")
        for plan in planes
    ]

    return success_response(
        data=build_paginated_response(
            items=items,
            total=total,
            page=page,
            limit=limit,
        ),
        message="Planes de estudio obtenidos correctamente",
    )


@router.get("/{plan_estudio_id}")
async def get_plan_estudio(
    plan_estudio_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    service = PlanEstudioService(db)
    plan = await service.get_plan_estudio(plan_estudio_id)

    return success_response(
        data=PlanEstudioRead.model_validate(plan).model_dump(mode="json"),
        message="Plan de estudio obtenido correctamente",
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_plan_estudio(
    payload: PlanEstudioCreate,
    db: AsyncSession = Depends(get_db),
):
    service = PlanEstudioService(db)
    plan = await service.create_plan_estudio(payload)

    return success_response(
        data=PlanEstudioRead.model_validate(plan).model_dump(mode="json"),
        message="Plan de estudio creado correctamente",
    )


@router.patch("/{plan_estudio_id}")
async def update_plan_estudio(
    plan_estudio_id: UUID,
    payload: PlanEstudioUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = PlanEstudioService(db)
    plan = await service.update_plan_estudio(plan_estudio_id, payload)

    return success_response(
        data=PlanEstudioRead.model_validate(plan).model_dump(mode="json"),
        message="Plan de estudio actualizado correctamente",
    )


@router.delete("/{plan_estudio_id}")
async def deactivate_plan_estudio(
    plan_estudio_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    service = PlanEstudioService(db)
    plan = await service.deactivate_plan_estudio(plan_estudio_id)

    return success_response(
        data=PlanEstudioRead.model_validate(plan).model_dump(mode="json"),
        message="Plan de estudio desactivado correctamente",
    )