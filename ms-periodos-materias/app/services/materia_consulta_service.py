from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import materia_consulta_repository
from app.schemas.materia_consulta import (
    MateriaAcademicaRead,
    MateriaCatalogoResumen,
    MateriaHorarioResumen,
    PeriodoResumen,
)


def _build_materia_academica_response(record) -> MateriaAcademicaRead:
    materia_ofertada, periodo, materia_catalogo, horarios = record

    return MateriaAcademicaRead(
        materia_ofertada_id=materia_ofertada.materia_ofertada_id,
        nrc=materia_ofertada.nrc,
        seccion=materia_ofertada.seccion,
        estado=materia_ofertada.estado,
        periodo=PeriodoResumen(
            periodo_id=periodo.periodo_id,
            nombre=periodo.nombre,
            fecha_inicio=periodo.fecha_inicio,
            fecha_fin=periodo.fecha_fin,
            activo=periodo.activo,
        ),
        materia=MateriaCatalogoResumen(
            materia_catalogo_id=materia_catalogo.materia_catalogo_id,
            clave=materia_catalogo.clave,
            nombre=materia_catalogo.nombre,
            activo=materia_catalogo.activo,
        ),
        docente_id=materia_ofertada.docente_id,
        docente_nombre=materia_ofertada.docente_nombre,
        horarios=[
            MateriaHorarioResumen(
                materia_horario_id=horario.materia_horario_id,
                dia=horario.dia,
                hora_inicio=horario.hora_inicio,
                hora_fin=horario.hora_fin,
                salon=horario.salon,
            )
            for horario in horarios
        ],
    )


async def get_periodo_activo(db: AsyncSession) -> PeriodoResumen:
    periodo = await materia_consulta_repository.get_periodo_activo(db)

    if periodo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No existe un periodo activo",
        )

    return PeriodoResumen(
        periodo_id=periodo.periodo_id,
        nombre=periodo.nombre,
        fecha_inicio=periodo.fecha_inicio,
        fecha_fin=periodo.fecha_fin,
        activo=periodo.activo,
    )


async def list_materias_academicas(
    db: AsyncSession,
    periodo_id: UUID | None = None,
    docente_id: UUID | None = None,
    estado: str | None = None,
    clave: str | None = None,
    nrc: str | None = None,
    page: int = 1,
    limit: int = 10,
) -> tuple[list[MateriaAcademicaRead], int]:
    estado_normalizado = estado.upper() if estado else None

    records, total = await materia_consulta_repository.list_materias_academicas(
        db=db,
        periodo_id=periodo_id,
        docente_id=docente_id,
        estado=estado_normalizado,
        clave=clave,
        nrc=nrc,
        page=page,
        limit=limit,
    )

    items = [_build_materia_academica_response(record) for record in records]

    return items, total


async def get_materia_academica_by_id(
    db: AsyncSession,
    materia_ofertada_id: UUID,
) -> MateriaAcademicaRead:
    record = await materia_consulta_repository.get_materia_academica_by_id(
        db=db,
        materia_ofertada_id=materia_ofertada_id,
    )

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Materia ofertada no encontrada",
        )

    return _build_materia_academica_response(record)


async def list_materias_by_periodo(
    db: AsyncSession,
    periodo_id: UUID,
    page: int = 1,
    limit: int = 10,
) -> tuple[list[MateriaAcademicaRead], int]:
    records, total = await materia_consulta_repository.list_materias_by_periodo(
        db=db,
        periodo_id=periodo_id,
        page=page,
        limit=limit,
    )

    items = [_build_materia_academica_response(record) for record in records]

    return items, total


async def list_materias_by_docente(
    db: AsyncSession,
    docente_id: UUID,
    page: int = 1,
    limit: int = 10,
) -> tuple[list[MateriaAcademicaRead], int]:
    records, total = await materia_consulta_repository.list_materias_by_docente(
        db=db,
        docente_id=docente_id,
        page=page,
        limit=limit,
    )

    items = [_build_materia_academica_response(record) for record in records]

    return items, total


async def list_materias_periodo_activo(
    db: AsyncSession,
    page: int = 1,
    limit: int = 10,
) -> tuple[list[MateriaAcademicaRead], int]:
    result = await materia_consulta_repository.list_materias_periodo_activo(
        db=db,
        page=page,
        limit=limit,
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No existe un periodo activo",
        )

    records, total = result

    items = [_build_materia_academica_response(record) for record in records]

    return items, total