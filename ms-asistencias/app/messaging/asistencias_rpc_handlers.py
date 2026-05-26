import logging
from datetime import datetime
from typing import Any

from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models.enums import EstadoAsistencia
from app.models.registro_asistencia import RegistroAsistencia
from app.models.sesion_asistencia import SesionAsistencia

logger = logging.getLogger(__name__)


def _string_value(value: Any) -> str:
    return str(value or "")


def _datetime_value(value: datetime | None) -> str:
    return value.isoformat() if value else ""


def _estado_value(registro: RegistroAsistencia) -> str:
    estado = registro.estado_asistencia
    return estado.value if hasattr(estado, "value") else str(estado)


def _asistencia_detalle_to_dict(registro: RegistroAsistencia) -> dict[str, Any]:
    fecha = _datetime_value(registro.fecha_hora_registro)
    return {
        "fecha": fecha,
        "fecha_registro": fecha,
        "estado": _estado_value(registro),
        "sesion_id": str(registro.id_sesion),
        "id_sesion": registro.id_sesion,
    }


async def get_asistencia_alumno_handler(payload: dict[str, Any]) -> dict[str, Any]:
    alumno_id = _string_value(payload.get("alumno_id") or payload.get("id_alumno"))
    materia_id = _string_value(payload.get("materia_id") or payload.get("id_materia"))

    if not alumno_id or not materia_id:
        return {
            "found": False,
            "alumno_id": alumno_id,
            "materia_id": materia_id,
            "asistencias": [],
            "total": 0,
            "total_presentes": 0,
            "total_retardos": 0,
            "porcentaje": 0,
            "error_code": "INVALID_PAYLOAD",
            "message": "alumno_id y materia_id son requeridos",
        }

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(RegistroAsistencia)
            .join(SesionAsistencia, RegistroAsistencia.id_sesion == SesionAsistencia.id_sesion)
            .where(
                RegistroAsistencia.id_alumno == alumno_id,
                SesionAsistencia.id_materia == materia_id,
            )
        )
        registros = result.scalars().all()

    detalles = [_asistencia_detalle_to_dict(registro) for registro in registros]
    presentes = sum(1 for registro in registros if registro.estado_asistencia == EstadoAsistencia.PRESENTE)
    retardos = sum(1 for registro in registros if registro.estado_asistencia == EstadoAsistencia.RETARDO)
    porcentaje = round(((presentes + retardos) / len(registros)) * 100, 2) if registros else 0

    if not registros:
        return {
            "found": False,
            "alumno_id": alumno_id,
            "materia_id": materia_id,
            "asistencias": [],
            "total": 0,
            "total_presentes": 0,
            "total_retardos": 0,
            "porcentaje": 0,
            "error_code": "ASISTENCIA_NOT_FOUND",
            "message": "No se encontro asistencia para el alumno",
        }

    return {
        "found": True,
        "alumno_id": alumno_id,
        "materia_id": materia_id,
        "asistencias": detalles,
        "total": len(detalles),
        "total_presentes": presentes,
        "total_retardos": retardos,
        "porcentaje": porcentaje,
        "error_code": "",
        "message": "Asistencia del alumno obtenida",
    }


async def get_asistencias_materia_handler(payload: dict[str, Any]) -> dict[str, Any]:
    materia_id = _string_value(payload.get("materia_id") or payload.get("id_materia"))

    if not materia_id:
        return {
            "found": False,
            "materia_id": materia_id,
            "asistencias": [],
            "total": 0,
            "error_code": "INVALID_PAYLOAD",
            "message": "materia_id es requerido",
        }

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(RegistroAsistencia)
            .join(SesionAsistencia, RegistroAsistencia.id_sesion == SesionAsistencia.id_sesion)
            .where(SesionAsistencia.id_materia == materia_id)
        )
        registros = result.scalars().all()

    resumen_alumnos: dict[str, dict[str, int]] = {}
    for registro in registros:
        alumno_id = str(registro.id_alumno)
        if alumno_id not in resumen_alumnos:
            resumen_alumnos[alumno_id] = {"presentes": 0, "retardos": 0, "faltas": 0}

        if registro.estado_asistencia == EstadoAsistencia.PRESENTE:
            resumen_alumnos[alumno_id]["presentes"] += 1
        elif registro.estado_asistencia == EstadoAsistencia.RETARDO:
            resumen_alumnos[alumno_id]["retardos"] += 1
        elif registro.estado_asistencia == EstadoAsistencia.AUSENTE:
            resumen_alumnos[alumno_id]["faltas"] += 1

    asistencias = []
    for alumno_id, data in resumen_alumnos.items():
        total_registros = data["presentes"] + data["retardos"] + data["faltas"]
        asistencias_validas = data["presentes"] + data["retardos"]
        porcentaje = round((asistencias_validas / total_registros) * 100, 2) if total_registros else 0
        asistencias.append(
            {
                "alumno_id": alumno_id,
                "id_alumno": alumno_id,
                "nombre_alumno": "",
                "presentes": data["presentes"],
                "total_presentes": data["presentes"],
                "retardos": data["retardos"],
                "total_retardos": data["retardos"],
                "faltas": data["faltas"],
                "porcentaje": porcentaje,
            }
        )

    return {
        "found": True,
        "materia_id": materia_id,
        "asistencias": asistencias,
        "total": len(asistencias),
        "error_code": "",
        "message": "Asistencias de materia obtenidas",
    }


async def get_estadisticas_asistencia_handler(payload: dict[str, Any]) -> dict[str, Any]:
    materia_id = _string_value(payload.get("materia_id") or payload.get("id_materia"))

    if not materia_id:
        return {
            "found": False,
            "materia_id": materia_id,
            "total_sesiones": 0,
            "total_sesiones_impartidas": 0,
            "promedio_asistencia": 0,
            "porcentaje_asistencia_general": 0,
            "alumnos_riesgo": 0,
            "total_alumnos": 0,
            "error_code": "INVALID_PAYLOAD",
            "message": "materia_id es requerido",
        }

    async with AsyncSessionLocal() as db:
        result_sesiones = await db.execute(
            select(SesionAsistencia).where(SesionAsistencia.id_materia == materia_id)
        )
        sesiones = result_sesiones.scalars().all()
        total_sesiones = len(sesiones)

        if total_sesiones == 0:
            return {
                "found": True,
                "materia_id": materia_id,
                "total_sesiones": 0,
                "total_sesiones_impartidas": 0,
                "promedio_asistencia": 0,
                "porcentaje_asistencia_general": 0,
                "alumnos_riesgo": 0,
                "total_alumnos": 0,
                "error_code": "",
                "message": "Estadisticas de asistencia obtenidas",
            }

        try:
            from app.messaging.clients.docentes_hybrid_client import cliente_alumnos

            alumnos_inscritos = await cliente_alumnos.obtener_alumnos_por_materia(materia_id)
            total_alumnos = len(alumnos_inscritos)
        except Exception as exc:
            logger.error("Error MS-3 en get_estadisticas_asistencia_handler: %s", exc)
            return {
                "found": False,
                "materia_id": materia_id,
                "total_sesiones": total_sesiones,
                "total_sesiones_impartidas": total_sesiones,
                "promedio_asistencia": 0,
                "porcentaje_asistencia_general": 0,
                "alumnos_riesgo": 0,
                "total_alumnos": 0,
                "error_code": "DOCENTES_SERVICE_UNAVAILABLE",
                "message": "No se pudo consultar el total de alumnos",
            }

        ids_sesiones = [sesion.id_sesion for sesion in sesiones]
        result_registros = await db.execute(
            select(RegistroAsistencia).where(RegistroAsistencia.id_sesion.in_(ids_sesiones))
        )
        registros = result_registros.scalars().all()

    presentes = sum(1 for registro in registros if registro.estado_asistencia == EstadoAsistencia.PRESENTE)
    retardos = sum(1 for registro in registros if registro.estado_asistencia == EstadoAsistencia.RETARDO)
    total_posibles_asistencias = total_alumnos * total_sesiones
    asistencias_validas = presentes + retardos
    porcentaje = 0.0
    if total_posibles_asistencias > 0:
        porcentaje = (asistencias_validas / total_posibles_asistencias) * 100.0

    promedio = round(porcentaje, 2)
    return {
        "found": True,
        "materia_id": materia_id,
        "total_sesiones": total_sesiones,
        "total_sesiones_impartidas": total_sesiones,
        "promedio_asistencia": promedio,
        "porcentaje_asistencia_general": promedio,
        "alumnos_riesgo": 0,
        "total_alumnos": total_alumnos,
        "error_code": "",
        "message": "Estadisticas de asistencia obtenidas",
    }
