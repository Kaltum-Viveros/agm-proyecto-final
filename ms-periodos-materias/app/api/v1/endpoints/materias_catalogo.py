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

router = APIRouter()


@router.get("")
async def list_materias_catalogo(
    activo: bool | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    service = MateriaCatalogoService(db)
    materias = await service.list_materias_catalogo(activo=activo)

    return success_response(
        data=[
            MateriaCatalogoRead.model_validate(materia).model_dump(mode="json")
            for materia in materias
        ],
        message="Materias del catálogo obtenidas correctamente",
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