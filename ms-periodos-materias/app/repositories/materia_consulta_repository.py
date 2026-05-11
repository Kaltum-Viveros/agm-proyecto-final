from collections import defaultdict
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.materia_catalogo import MateriaCatalogo
from app.models.materia_horario import MateriaHorario
from app.models.materia_ofertada import MateriaOfertada
from app.models.periodo import Periodo


async def get_periodo_activo(db: AsyncSession) -> Periodo | None:
    result = await db.execute(
        select(Periodo)
        .where(Periodo.activo.is_(True))
        .limit(1)
    )
    return result.scalar_one_or_none()


async def _get_horarios_by_ofertas(
    db: AsyncSession,
    materia_ofertada_ids: list[UUID],
) -> dict[UUID, list[MateriaHorario]]:
    if not materia_ofertada_ids:
        return {}

    result = await db.execute(
        select(MateriaHorario)
        .where(MateriaHorario.materia_ofertada_id.in_(materia_ofertada_ids))
        .order_by(
            MateriaHorario.materia_ofertada_id,
            MateriaHorario.dia,
            MateriaHorario.hora_inicio,
        )
    )

    horarios_by_oferta: dict[UUID, list[MateriaHorario]] = defaultdict(list)

    for horario in result.scalars().all():
        horarios_by_oferta[horario.materia_ofertada_id].append(horario)

    return horarios_by_oferta


async def list_materias_academicas(
    db: AsyncSession,
    periodo_id: UUID | None = None,
    docente_id: UUID | None = None,
    estado: str | None = None,
) -> list[tuple[MateriaOfertada, Periodo, MateriaCatalogo, list[MateriaHorario]]]:
    stmt = (
        select(MateriaOfertada, Periodo, MateriaCatalogo)
        .join(Periodo, MateriaOfertada.periodo_id == Periodo.periodo_id)
        .join(
            MateriaCatalogo,
            MateriaOfertada.materia_catalogo_id == MateriaCatalogo.materia_catalogo_id,
        )
    )

    if periodo_id is not None:
        stmt = stmt.where(MateriaOfertada.periodo_id == periodo_id)

    if docente_id is not None:
        stmt = stmt.where(MateriaOfertada.docente_id == docente_id)

    if estado is not None:
        stmt = stmt.where(MateriaOfertada.estado == estado)

    stmt = stmt.order_by(
        Periodo.nombre,
        MateriaCatalogo.nombre,
        MateriaOfertada.seccion,
    )

    result = await db.execute(stmt)
    rows = result.all()

    materia_ofertada_ids = [row[0].materia_ofertada_id for row in rows]
    horarios_by_oferta = await _get_horarios_by_ofertas(db, materia_ofertada_ids)

    return [
        (
            materia_ofertada,
            periodo,
            materia_catalogo,
            horarios_by_oferta.get(materia_ofertada.materia_ofertada_id, []),
        )
        for materia_ofertada, periodo, materia_catalogo in rows
    ]


async def get_materia_academica_by_id(
    db: AsyncSession,
    materia_ofertada_id: UUID,
) -> tuple[MateriaOfertada, Periodo, MateriaCatalogo, list[MateriaHorario]] | None:
    result = await db.execute(
        select(MateriaOfertada, Periodo, MateriaCatalogo)
        .join(Periodo, MateriaOfertada.periodo_id == Periodo.periodo_id)
        .join(
            MateriaCatalogo,
            MateriaOfertada.materia_catalogo_id == MateriaCatalogo.materia_catalogo_id,
        )
        .where(MateriaOfertada.materia_ofertada_id == materia_ofertada_id)
        .limit(1)
    )

    row = result.first()

    if row is None:
        return None

    materia_ofertada, periodo, materia_catalogo = row

    horarios_by_oferta = await _get_horarios_by_ofertas(
        db,
        [materia_ofertada.materia_ofertada_id],
    )

    return (
        materia_ofertada,
        periodo,
        materia_catalogo,
        horarios_by_oferta.get(materia_ofertada.materia_ofertada_id, []),
    )


async def list_materias_by_periodo(
    db: AsyncSession,
    periodo_id: UUID,
) -> list[tuple[MateriaOfertada, Periodo, MateriaCatalogo, list[MateriaHorario]]]:
    return await list_materias_academicas(db=db, periodo_id=periodo_id)


async def list_materias_by_docente(
    db: AsyncSession,
    docente_id: UUID,
) -> list[tuple[MateriaOfertada, Periodo, MateriaCatalogo, list[MateriaHorario]]]:
    return await list_materias_academicas(db=db, docente_id=docente_id)


async def list_materias_periodo_activo(
    db: AsyncSession,
) -> list[tuple[MateriaOfertada, Periodo, MateriaCatalogo, list[MateriaHorario]]] | None:
    periodo_activo = await get_periodo_activo(db)

    if periodo_activo is None:
        return None

    return await list_materias_by_periodo(
        db=db,
        periodo_id=periodo_activo.periodo_id,
    )