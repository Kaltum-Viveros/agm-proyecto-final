import logging
from decimal import Decimal
from typing import Any
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import func, select

from app.db.session import SessionLocal
from app.grpc.services.calificaciones_grpc_service import CalificacionesGrpcService
from app.models.actividad import Actividad
from app.models.calificacion import Calificacion

logger = logging.getLogger(__name__)


def _parse_uuid(value: Any) -> UUID | None:
    try:
        return UUID(str(value))
    except (TypeError, ValueError):
        return None


def _normalizar_modo(value: Any) -> str:
    modo = str(value or "actual").strip().lower()
    return modo if modo in ("actual", "final") else "actual"


def _json_value(value: Any) -> Any:
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, list):
        return [_json_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _json_value(item) for key, item in value.items()}
    return value


def _detalle_ponderacion_to_dict(detalle: dict[str, Any]) -> dict[str, Any]:
    return {
        "ponderacion_id": str(detalle["ponderacion_id"]),
        "nombre": detalle["nombre"],
        "porcentaje": float(detalle["porcentaje"]),
        "total_actividades": int(detalle["total_actividades"]),
        "actividades_calificadas": int(detalle["actividades_calificadas"]),
        "promedio_criterio": float(detalle["promedio_criterio"]),
        "aporte": float(detalle["aporte"]),
        "incluida_en_calculo": bool(detalle["incluida_en_calculo"]),
    }


def _alumno_concentrado_to_dict(alumno: dict[str, Any]) -> dict[str, Any]:
    promedio_redondeado = int(alumno["promedio_redondeado"])
    return {
        "alumno_id": str(alumno["alumno_id"]),
        "nombre_alumno": "",
        "modo": alumno["modo"],
        "peso_considerado": float(alumno["peso_considerado"]),
        "promedio_real": float(alumno["promedio_real"]),
        "promedio_redondeado": promedio_redondeado,
        "calificacion_final": promedio_redondeado,
        "estatus": "aprobado" if promedio_redondeado >= 6 else "reprobado",
        "detalle_ponderaciones": [
            _detalle_ponderacion_to_dict(detalle)
            for detalle in alumno["detalle_ponderaciones"]
        ],
    }


def _ponderacion_to_dict(ponderacion: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(ponderacion["id"]),
        "materia_id": str(ponderacion["materia_id"]),
        "nombre": ponderacion["nombre"],
        "porcentaje": float(ponderacion["porcentaje"]),
        "orden": int(ponderacion["orden"]),
    }


def _obtener_concentrado(materia_id: UUID, modo: str) -> dict[str, Any]:
    service = CalificacionesGrpcService()
    return service._obtener_concentrado_data(materia_id=materia_id, modo=modo)


def get_concentrado_handler(payload: dict[str, Any]) -> dict[str, Any]:
    materia_id = _parse_uuid(payload.get("materia_id"))
    modo = _normalizar_modo(payload.get("modo"))

    if materia_id is None:
        return {
            "found": False,
            "materia_id": str(payload.get("materia_id") or ""),
            "concentrado": [],
            "total": 0,
            "error_code": "INVALID_MATERIA_ID",
            "message": "materia_id no es un UUID valido",
        }

    try:
        data = _obtener_concentrado(materia_id=materia_id, modo=modo)
        alumnos = [_alumno_concentrado_to_dict(alumno) for alumno in data["alumnos"]]
        return {
            "found": True,
            "materia_id": str(data["materia_id"]),
            "modo": data["modo"],
            "concentrado": alumnos,
            "alumnos": alumnos,
            "ponderaciones": [
                _ponderacion_to_dict(ponderacion)
                for ponderacion in data["ponderaciones"]
            ],
            "total": len(alumnos),
            "total_alumnos": int(data["total_alumnos"]),
            "error_code": "",
            "message": "Concentrado obtenido",
        }
    except HTTPException as exc:
        return {
            "found": False,
            "materia_id": str(materia_id),
            "modo": modo,
            "concentrado": [],
            "alumnos": [],
            "ponderaciones": [],
            "total": 0,
            "total_alumnos": 0,
            "error_code": "CONCENTRADO_NOT_FOUND" if exc.status_code == 404 else "CONCENTRADO_ERROR",
            "message": str(exc.detail),
        }
    except Exception as exc:
        logger.exception("Error en get_concentrado_handler")
        return {
            "found": False,
            "materia_id": str(materia_id),
            "modo": modo,
            "concentrado": [],
            "alumnos": [],
            "ponderaciones": [],
            "total": 0,
            "total_alumnos": 0,
            "error_code": "INTERNAL_ERROR",
            "message": str(exc),
        }


def get_promedio_alumno_handler(payload: dict[str, Any]) -> dict[str, Any]:
    alumno_id = _parse_uuid(payload.get("alumno_id"))
    materia_id = _parse_uuid(payload.get("materia_id")) if payload.get("materia_id") else None
    modo = _normalizar_modo(payload.get("modo"))

    if alumno_id is None:
        return {
            "found": False,
            "alumno_id": str(payload.get("alumno_id") or ""),
            "promedio": 0,
            "materias": 0,
            "error_code": "INVALID_ALUMNO_ID",
            "message": "alumno_id no es un UUID valido",
        }

    if materia_id is not None:
        try:
            data = _obtener_concentrado(materia_id=materia_id, modo=modo)
            alumno = next(
                (item for item in data["alumnos"] if item["alumno_id"] == alumno_id),
                None,
            )
            if alumno is None:
                return {
                    "found": False,
                    "alumno_id": str(alumno_id),
                    "materia_id": str(materia_id),
                    "promedio": 0,
                    "materias": 0,
                    "error_code": "PROMEDIO_NOT_FOUND",
                    "message": "No existen calificaciones para el alumno en esta materia",
                }

            alumno_data = _alumno_concentrado_to_dict(alumno)
            return {
                "found": True,
                "alumno_id": str(alumno_id),
                "materia_id": str(materia_id),
                "modo": modo,
                "promedio": alumno_data["promedio_real"],
                "promedio_real": alumno_data["promedio_real"],
                "promedio_redondeado": alumno_data["promedio_redondeado"],
                "materias": 1,
                "detalle_ponderaciones": alumno_data["detalle_ponderaciones"],
                "error_code": "",
                "message": "Promedio obtenido",
            }
        except HTTPException as exc:
            return {
                "found": False,
                "alumno_id": str(alumno_id),
                "materia_id": str(materia_id),
                "promedio": 0,
                "materias": 0,
                "error_code": "PROMEDIO_NOT_FOUND" if exc.status_code == 404 else "PROMEDIO_ERROR",
                "message": str(exc.detail),
            }

    db = SessionLocal()
    try:
        rows = db.execute(
            select(
                func.avg(Calificacion.calificacion),
                func.count(func.distinct(Actividad.materia_id)),
            )
            .join(Actividad, Calificacion.actividad_id == Actividad.id)
            .where(Calificacion.alumno_id == alumno_id)
        ).one()
        promedio = rows[0]
        materias = int(rows[1] or 0)
        if promedio is None or materias == 0:
            return {
                "found": False,
                "alumno_id": str(alumno_id),
                "promedio": 0,
                "materias": 0,
                "error_code": "PROMEDIO_NOT_FOUND",
                "message": "No existen calificaciones para el alumno",
            }

        return {
            "found": True,
            "alumno_id": str(alumno_id),
            "promedio": round(float(promedio), 2),
            "promedio_real": round(float(promedio), 2),
            "materias": materias,
            "error_code": "",
            "message": "Promedio obtenido",
        }
    except Exception as exc:
        logger.exception("Error en get_promedio_alumno_handler")
        return {
            "found": False,
            "alumno_id": str(alumno_id),
            "promedio": 0,
            "materias": 0,
            "error_code": "INTERNAL_ERROR",
            "message": str(exc),
        }
    finally:
        db.close()


def get_estadisticas_materia_handler(payload: dict[str, Any]) -> dict[str, Any]:
    materia_id = _parse_uuid(payload.get("materia_id"))
    modo = _normalizar_modo(payload.get("modo"))

    if materia_id is None:
        return {
            "found": False,
            "materia_id": str(payload.get("materia_id") or ""),
            "promedio": 0,
            "aprobados": 0,
            "reprobados": 0,
            "total_alumnos": 0,
            "error_code": "INVALID_MATERIA_ID",
            "message": "materia_id no es un UUID valido",
        }

    try:
        data = _obtener_concentrado(materia_id=materia_id, modo=modo)
        alumnos = data["alumnos"]
        if not alumnos:
            return {
                "found": True,
                "materia_id": str(materia_id),
                "modo": modo,
                "promedio": 0,
                "promedio_grupal": 0,
                "aprobados": 0,
                "reprobados": 0,
                "total_alumnos": 0,
                "promedio_minimo": 0,
                "promedio_maximo": 0,
                "error_code": "",
                "message": "Estadisticas obtenidas",
            }

        promedios = [float(alumno["promedio_real"]) for alumno in alumnos]
        aprobados = sum(1 for alumno in alumnos if int(alumno["promedio_redondeado"]) >= 6)
        reprobados = len(alumnos) - aprobados
        promedio_grupal = round(sum(promedios) / len(promedios), 2)

        return {
            "found": True,
            "materia_id": str(materia_id),
            "modo": modo,
            "promedio": promedio_grupal,
            "promedio_grupal": promedio_grupal,
            "aprobados": aprobados,
            "reprobados": reprobados,
            "total_alumnos": len(alumnos),
            "promedio_minimo": round(min(promedios), 2),
            "promedio_maximo": round(max(promedios), 2),
            "error_code": "",
            "message": "Estadisticas obtenidas",
        }
    except HTTPException as exc:
        return {
            "found": False,
            "materia_id": str(materia_id),
            "modo": modo,
            "promedio": 0,
            "promedio_grupal": 0,
            "aprobados": 0,
            "reprobados": 0,
            "total_alumnos": 0,
            "error_code": "ESTADISTICAS_NOT_FOUND" if exc.status_code == 404 else "ESTADISTICAS_ERROR",
            "message": str(exc.detail),
        }
    except Exception as exc:
        logger.exception("Error en get_estadisticas_materia_handler")
        return {
            "found": False,
            "materia_id": str(materia_id),
            "modo": modo,
            "promedio": 0,
            "promedio_grupal": 0,
            "aprobados": 0,
            "reprobados": 0,
            "total_alumnos": 0,
            "error_code": "INTERNAL_ERROR",
            "message": str(exc),
        }
