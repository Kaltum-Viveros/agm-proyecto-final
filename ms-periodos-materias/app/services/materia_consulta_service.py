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
) -> list[MateriaAcademicaRead]:
    estado_normalizado = estado.upper() if estado else None

    records = await materia_consulta_repository.list_materias_academicas(
        db=db,
        periodo_id=periodo_id,
        docente_id=docente_id,
        estado=estado_normalizado,
    )

    return [_build_materia_academica_response(record) for record in records]


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
) -> list[MateriaAcademicaRead]:
    records = await materia_consulta_repository.list_materias_by_periodo(
        db=db,
        periodo_id=periodo_id,
    )

    return [_build_materia_academica_response(record) for record in records]


async def list_materias_by_docente(
    db: AsyncSession,
    docente_id: UUID,
) -> list[MateriaAcademicaRead]:
    records = await materia_consulta_repository.list_materias_by_docente(
        db=db,
        docente_id=docente_id,
    )

    return [_build_materia_academica_response(record) for record in records]


async def list_materias_periodo_activo(
    db: AsyncSession,
) -> list[MateriaAcademicaRead]:
    records = await materia_consulta_repository.list_materias_periodo_activo(db)

    if records is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No existe un periodo activo",
        )

    return [_build_materia_academica_response(record) for record in records]