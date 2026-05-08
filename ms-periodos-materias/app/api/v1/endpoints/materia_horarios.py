from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.responses import success_response
from app.db.session import get_db
from app.schemas.materia_horario import (
    MateriaHorarioCreate,
    MateriaHorarioRead,
    MateriaHorarioUpdate,
)
from app.services.materia_horario_service import MateriaHorarioService

router = APIRouter()


@router.get("")
async def list_materia_horarios(
    materia_ofertada_id: UUID | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    service = MateriaHorarioService(db)
    horarios = await service.list_horarios(materia_ofertada_id=materia_ofertada_id)

    return success_response(
        data=[
            MateriaHorarioRead.model_validate(horario).model_dump(mode="json")
            for horario in horarios
        ],
        message="Horarios de materia obtenidos correctamente",
    )


@router.get("/{materia_horario_id}")
async def get_materia_horario(
    materia_horario_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    service = MateriaHorarioService(db)
    horario = await service.get_horario(materia_horario_id)

    return success_response(
        data=MateriaHorarioRead.model_validate(horario).model_dump(mode="json"),
        message="Horario de materia obtenido correctamente",
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_materia_horario(
    payload: MateriaHorarioCreate,
    db: AsyncSession = Depends(get_db),
):
    service = MateriaHorarioService(db)
    horario = await service.create_horario(payload)

    return success_response(
        data=MateriaHorarioRead.model_validate(horario).model_dump(mode="json"),
        message="Horario de materia creado correctamente",
    )


@router.patch("/{materia_horario_id}")
async def update_materia_horario(
    materia_horario_id: UUID,
    payload: MateriaHorarioUpdate,
    db: AsyncSession = Depends(get_db),
):
    service = MateriaHorarioService(db)
    horario = await service.update_horario(materia_horario_id, payload)

    return success_response(
        data=MateriaHorarioRead.model_validate(horario).model_dump(mode="json"),
        message="Horario de materia actualizado correctamente",
    )


@router.delete("/{materia_horario_id}")
async def delete_materia_horario(
    materia_horario_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    service = MateriaHorarioService(db)
    await service.delete_horario(materia_horario_id)

    return success_response(
        data=None,
        message="Horario de materia eliminado correctamente",
    )