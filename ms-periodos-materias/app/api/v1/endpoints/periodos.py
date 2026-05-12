from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.responses import success_response
from app.db.session import get_db
from app.schemas.periodo import PeriodoCreate, PeriodoRead, PeriodoUpdate
from app.services.periodo_service import PeriodoService
from app.services import materia_consulta_service
from app.core.pagination import build_paginated_response

router = APIRouter()

@router.get("")
async def list_periodos(
    activo: bool | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    service = PeriodoService(db)
    periodos, total = await service.list_periodos(
        activo=activo,
        page=page,
        limit=limit,
    )

    items = [
        PeriodoRead.model_validate(periodo).model_dump(mode="json")
        for periodo in periodos
    ]

    return success_response(
        data=build_paginated_response(
            items=items,
            total=total,
            page=page,
            limit=limit,
        ),
        message="Periodos obtenidos correctamente",
    )

@router.get("/activo")
async def get_periodo_activo(
    db: AsyncSession = Depends(get_db),
):
    data = await materia_consulta_service.get_periodo_activo(db)

    return success_response(
        data=data.model_dump(mode="json"),
        message="Periodo activo obtenido correctamente",
    )


@router.get("/{periodo_id}")
async def get_periodo(
    periodo_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    service = PeriodoService(db)
    periodo = await service.get_periodo(periodo_id)

    return success_response(
        data=PeriodoRead.model_validate(periodo).model_dump(mode="json"),
        message="Periodo obtenido correctamente",
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_periodo(
    payload: PeriodoCreate,
    db: AsyncSession = Depends(get_db),
):
    service = PeriodoService(db)
    periodo = await service.create_periodo(payload)

    return success_response(
        data=PeriodoRead.model_validate(periodo).model_dump(mode="json"),
        message="Periodo creado correctamente",
    )


@router.patch("/{periodo_id}")
async def update_periodo(
    periodo_id: UUID,
    payload: PeriodoUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = PeriodoService(db)
    periodo = await service.update_periodo(periodo_id, payload)

    return success_response(
        data=PeriodoRead.model_validate(periodo).model_dump(mode="json"),
        message="Periodo actualizado correctamente",
    )


@router.delete("/{periodo_id}")
async def deactivate_periodo(
    periodo_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    service = PeriodoService(db)
    periodo = await service.deactivate_periodo(periodo_id)

    return success_response(
        data=PeriodoRead.model_validate(periodo).model_dump(mode="json"),
        message="Periodo desactivado correctamente",
    )

@router.patch("/{periodo_id}/activar")
async def activar_periodo(
    periodo_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    service = PeriodoService(db)
    periodo = await service.activar_periodo(periodo_id)

    return success_response(
        data=PeriodoRead.model_validate(periodo).model_dump(mode="json"),
        message="Periodo activado correctamente",
    )