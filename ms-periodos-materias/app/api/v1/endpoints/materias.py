from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services import materia_consulta_service

router = APIRouter()


@router.get("")
async def list_materias(
    periodo: UUID | None = Query(
        default=None,
        description="Filtra materias por periodo_id. Equivale a /materias?periodo=:id",
    ),
    docente_id: UUID | None = Query(
        default=None,
        description="Filtra materias por docente_id externo del MS-3",
    ),
    estado: str | None = Query(
        default=None,
        description="Filtra por estado de la materia ofertada. Ejemplo: ACTIVA",
    ),
    db: AsyncSession = Depends(get_db),
):
    data = await materia_consulta_service.list_materias_academicas(
        db=db,
        periodo_id=periodo,
        docente_id=docente_id,
        estado=estado,
    )

    return {
        "success": True,
        "data": data,
        "message": "Materias académicas obtenidas correctamente",
    }


@router.get("/periodo-activo")
async def list_materias_periodo_activo(
    db: AsyncSession = Depends(get_db),
):
    data = await materia_consulta_service.list_materias_periodo_activo(db)

    return {
        "success": True,
        "data": data,
        "message": "Materias del periodo activo obtenidas correctamente",
    }


@router.get("/periodo/{periodo_id}")
async def list_materias_by_periodo(
    periodo_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    data = await materia_consulta_service.list_materias_by_periodo(
        db=db,
        periodo_id=periodo_id,
    )

    return {
        "success": True,
        "data": data,
        "message": "Materias del periodo obtenidas correctamente",
    }


@router.get("/docente/{docente_id}")
async def list_materias_by_docente(
    docente_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    data = await materia_consulta_service.list_materias_by_docente(
        db=db,
        docente_id=docente_id,
    )

    return {
        "success": True,
        "data": data,
        "message": "Materias del docente obtenidas correctamente",
    }


@router.get("/{materia_ofertada_id}")
async def get_materia_by_id(
    materia_ofertada_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    data = await materia_consulta_service.get_materia_academica_by_id(
        db=db,
        materia_ofertada_id=materia_ofertada_id,
    )

    return {
        "success": True,
        "data": data,
        "message": "Materia académica obtenida correctamente",
    }