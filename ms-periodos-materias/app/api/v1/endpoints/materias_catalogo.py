from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.responses import success_response
from app.db.session import get_db
from app.schemas.materia_catalogo import (
    MateriaCatalogoCreate,
    MateriaCatalogoRead,
    MateriaCatalogoUpdate,
)
from app.services.materia_catalogo_service import MateriaCatalogoService
from app.core.pagination import build_paginated_response

router = APIRouter()


@router.get("")
async def list_materias_catalogo(
    activo: bool | None = Query(default=None),
    clave: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    service = MateriaCatalogoService(db)
    materias, total = await service.list_materias_catalogo(
        activo=activo,
        clave=clave,
        page=page,
        limit=limit,
    )

    items = [
        MateriaCatalogoRead.model_validate(materia).model_dump(mode="json")
        for materia in materias
    ]

    return success_response(
        data=build_paginated_response(
            items=items,
            total=total,
            page=page,
            limit=limit,
        ),
        message="Materias de catálogo obtenidas correctamente",
    )


@router.get("/{materia_catalogo_id}")
async def get_materia_catalogo(
    materia_catalogo_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    service = MateriaCatalogoService(db)
    materia = await service.get_materia_catalogo(materia_catalogo_id)

    return success_response(
        data=MateriaCatalogoRead.model_validate(materia).model_dump(mode="json"),
        message="Materia del catálogo obtenida correctamente",
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_materia_catalogo(
    payload: MateriaCatalogoCreate,
    db: AsyncSession = Depends(get_db),
):
    service = MateriaCatalogoService(db)
    materia = await service.create_materia_catalogo(payload)

    return success_response(
        data=MateriaCatalogoRead.model_validate(materia).model_dump(mode="json"),
        message="Materia del catálogo creada correctamente",
    )


@router.patch("/{materia_catalogo_id}")
async def update_materia_catalogo(
    materia_catalogo_id: UUID,
    payload: MateriaCatalogoUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = MateriaCatalogoService(db)
    materia = await service.update_materia_catalogo(materia_catalogo_id, payload)

    return success_response(
        data=MateriaCatalogoRead.model_validate(materia).model_dump(mode="json"),
        message="Materia del catálogo actualizada correctamente",
    )


@router.delete("/{materia_catalogo_id}")
async def deactivate_materia_catalogo(
    materia_catalogo_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    service = MateriaCatalogoService(db)
    materia = await service.deactivate_materia_catalogo(materia_catalogo_id)

    return success_response(
        data=MateriaCatalogoRead.model_validate(materia).model_dump(mode="json"),
        message="Materia del catálogo desactivada correctamente",
    )