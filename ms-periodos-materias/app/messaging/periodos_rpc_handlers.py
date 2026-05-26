from typing import Any
from uuid import UUID

from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models.materia_catalogo import MateriaCatalogo
from app.models.materia_horario import MateriaHorario
from app.models.materia_ofertada import MateriaOfertada
from app.models.periodo import Periodo


def _to_str(value: Any) -> str:
    return "" if value is None else str(value)


def _date_to_str(value: Any) -> str:
    return "" if value is None else value.isoformat()


def _time_to_str(value: Any) -> str:
    return "" if value is None else value.isoformat()


def _parse_uuid(value: Any) -> UUID | None:
    try:
        return UUID(str(value))
    except (TypeError, ValueError):
        return None


def _periodo_to_dict(periodo: Periodo | None) -> dict[str, Any] | None:
    if periodo is None:
        return None

    return {
        "periodo_id": _to_str(periodo.periodo_id),
        "nombre": _to_str(periodo.nombre),
        "fecha_inicio": _date_to_str(periodo.fecha_inicio),
        "fecha_fin": _date_to_str(periodo.fecha_fin),
        "activo": bool(periodo.activo),
    }


async def _materia_to_dict(db, materia_ofertada: MateriaOfertada) -> dict[str, Any]:
    periodo = await db.get(Periodo, materia_ofertada.periodo_id)
    materia_catalogo = await db.get(
        MateriaCatalogo,
        materia_ofertada.materia_catalogo_id,
    )

    horarios_result = await db.execute(
        select(MateriaHorario)
        .where(MateriaHorario.materia_ofertada_id == materia_ofertada.materia_ofertada_id)
        .order_by(MateriaHorario.dia.asc(), MateriaHorario.hora_inicio.asc())
    )
    horarios = horarios_result.scalars().all()

    periodo_data = _periodo_to_dict(periodo)
    materia_catalogo_data = {
        "materia_catalogo_id": _to_str(getattr(materia_catalogo, "materia_catalogo_id", "")),
        "clave": _to_str(getattr(materia_catalogo, "clave", "")),
        "nombre": _to_str(getattr(materia_catalogo, "nombre", "")),
    }

    return {
        "materia_id": _to_str(materia_ofertada.materia_ofertada_id),
        "materia_ofertada_id": _to_str(materia_ofertada.materia_ofertada_id),
        "materia_catalogo_id": materia_catalogo_data["materia_catalogo_id"],
        "clave": materia_catalogo_data["clave"],
        "nombre": materia_catalogo_data["nombre"],
        "nrc": _to_str(materia_ofertada.nrc),
        "seccion": _to_str(materia_ofertada.seccion),
        "docente_id": _to_str(materia_ofertada.docente_id),
        "docente_nombre": _to_str(materia_ofertada.docente_nombre),
        "periodo_id": _to_str(materia_ofertada.periodo_id),
        "estado": _to_str(materia_ofertada.estado),
        "periodo": periodo_data or {},
        "materia": materia_catalogo_data,
        "horarios": [
            {
                "materia_horario_id": _to_str(horario.materia_horario_id),
                "dia": _to_str(horario.dia),
                "hora_inicio": _time_to_str(horario.hora_inicio),
                "hora_fin": _time_to_str(horario.hora_fin),
                "salon": _to_str(horario.salon),
            }
            for horario in horarios
        ],
    }


async def get_materia_by_id_handler(payload: dict[str, Any]) -> dict[str, Any]:
    materia_id = _parse_uuid(payload.get("materia_id"))
    if materia_id is None:
        return {
            "found": False,
            "materia": None,
            "error_code": "INVALID_MATERIA_ID",
            "message": "materia_id no es un UUID valido",
        }

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(MateriaOfertada)
            .where(MateriaOfertada.materia_ofertada_id == materia_id)
        )
        materia_ofertada = result.scalar_one_or_none()

        if materia_ofertada is None:
            return {
                "found": False,
                "materia": None,
                "error_code": "MATERIA_NOT_FOUND",
                "message": "Materia no encontrada",
            }

        return {
            "found": True,
            "materia": await _materia_to_dict(db, materia_ofertada),
            "error_code": "",
            "message": "Materia encontrada",
        }


async def get_materia_by_nrc_handler(payload: dict[str, Any]) -> dict[str, Any]:
    nrc = str(payload.get("nrc") or "").strip()
    if not nrc:
        return {
            "found": False,
            "materia": None,
            "error_code": "INVALID_NRC",
            "message": "nrc es requerido",
        }

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(MateriaOfertada)
            .where(MateriaOfertada.nrc == nrc)
            .limit(1)
        )
        materia_ofertada = result.scalar_one_or_none()

        if materia_ofertada is None:
            return {
                "found": False,
                "materia": None,
                "error_code": "MATERIA_NOT_FOUND",
                "message": "Materia no encontrada",
            }

        return {
            "found": True,
            "materia": await _materia_to_dict(db, materia_ofertada),
            "error_code": "",
            "message": "Materia encontrada",
        }


async def get_materias_by_docente_handler(payload: dict[str, Any]) -> dict[str, Any]:
    docente_id = _parse_uuid(payload.get("docente_id"))
    if docente_id is None:
        return {
            "materias": [],
            "total": 0,
            "error_code": "INVALID_DOCENTE_ID",
            "message": "docente_id no es un UUID valido",
        }

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(MateriaOfertada)
            .where(MateriaOfertada.docente_id == docente_id)
            .order_by(MateriaOfertada.nrc.asc())
        )
        materias_ofertadas = result.scalars().all()
        materias = [
            await _materia_to_dict(db, materia_ofertada)
            for materia_ofertada in materias_ofertadas
        ]

        return {
            "materias": materias,
            "total": len(materias),
            "error_code": "",
            "message": "Materias obtenidas",
        }


async def get_periodo_activo_handler(payload: dict[str, Any]) -> dict[str, Any]:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Periodo)
            .where(Periodo.activo.is_(True))
            .limit(1)
        )
        periodo = result.scalar_one_or_none()

        if periodo is None:
            return {
                "found": False,
                "periodo": None,
                "error_code": "PERIODO_ACTIVO_NOT_FOUND",
                "message": "No hay periodo activo",
            }

        return {
            "found": True,
            "periodo": _periodo_to_dict(periodo),
            "error_code": "",
            "message": "Periodo activo encontrado",
        }
