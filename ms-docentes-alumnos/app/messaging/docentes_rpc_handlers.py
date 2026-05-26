import logging
import unicodedata
from typing import Any, Dict

from app.db.session import SessionLocal
from app.models.alumno import Alumno
from app.models.docente import Docente
from app.models.inscripcion import Inscripcion

logger = logging.getLogger(__name__)


def _normalizar(texto: str) -> str:
    if not texto:
        return ""
    texto = unicodedata.normalize("NFD", texto)
    texto = texto.encode("ascii", "ignore").decode("utf-8")
    return texto.upper().strip()


def _alumno_to_dict(alumno: Alumno) -> Dict[str, Any]:
    return {
        "alumno_id": str(alumno.alumno_id),
        "user_id": str(alumno.user_id) if alumno.user_id else "",
        "nombre_completo": alumno.nombre_completo,
        "matricula": alumno.matricula,
        "correo": alumno.correo,
        "email": alumno.correo,
        "activo": bool(alumno.estatus_academico),
    }


def _docente_to_dict(docente: Docente) -> Dict[str, Any]:
    return {
        "docente_id": str(docente.docente_id),
        "user_id": str(docente.user_id) if docente.user_id else "",
        "nombre_completo": docente.nombre_completo,
        "correo": docente.correo,
        "email": docente.correo,
        "activo": bool(docente.estatus_laboral),
    }


def _materia_from_inscripcion(inscripcion: Inscripcion) -> Dict[str, Any]:
    return {
        "materia_id": str(inscripcion.materia_id),
        "nrc": inscripcion.nrc_materia,
        "nombre": "",
        "periodo_id": str(inscripcion.periodo_id),
        "seccion": inscripcion.seccion_materia or "",
    }


async def get_alumnos_by_materia_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    materia_id = payload.get("materia_id")
    if not materia_id:
        return {
            "alumnos": [],
            "total": 0,
            "error_code": "MISSING_MATERIA_ID",
            "message": "materia_id es requerido",
        }

    db = SessionLocal()
    try:
        inscripciones = (
            db.query(Inscripcion)
            .filter(
                Inscripcion.materia_id == materia_id,
                Inscripcion.activa == True,
            )
            .all()
        )
        alumnos = [
            _alumno_to_dict(inscripcion.alumno)
            for inscripcion in inscripciones
            if inscripcion.alumno
        ]
        return {
            "alumnos": alumnos,
            "total": len(alumnos),
            "error_code": "",
            "message": "Alumnos obtenidos",
        }
    except Exception as exc:
        logger.exception("Error en get_alumnos_by_materia_handler")
        return {
            "alumnos": [],
            "total": 0,
            "error_code": "INTERNAL_ERROR",
            "message": str(exc),
        }
    finally:
        db.close()


async def is_alumno_en_materia_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    alumno_id = payload.get("alumno_id")
    materia_id = payload.get("materia_id")
    if not alumno_id or not materia_id:
        return {
            "enrolled": False,
            "error_code": "MISSING_IDS",
            "message": "alumno_id y materia_id son requeridos",
        }

    db = SessionLocal()
    try:
        enrolled = (
            db.query(Inscripcion)
            .filter(
                Inscripcion.alumno_id == alumno_id,
                Inscripcion.materia_id == materia_id,
                Inscripcion.activa == True,
            )
            .first()
            is not None
        )
        return {
            "enrolled": enrolled,
            "error_code": "",
            "message": (
                "Alumno inscrito en materia"
                if enrolled
                else "Alumno no inscrito en materia"
            ),
        }
    except Exception as exc:
        logger.exception("Error en is_alumno_en_materia_handler")
        return {
            "enrolled": False,
            "error_code": "INTERNAL_ERROR",
            "message": str(exc),
        }
    finally:
        db.close()


async def get_materias_by_alumno_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    alumno_id = payload.get("alumno_id")
    if not alumno_id:
        return {
            "materias": [],
            "total": 0,
            "error_code": "MISSING_ALUMNO_ID",
            "message": "alumno_id es requerido",
        }

    db = SessionLocal()
    try:
        inscripciones = (
            db.query(Inscripcion)
            .filter(
                Inscripcion.alumno_id == alumno_id,
                Inscripcion.activa == True,
            )
            .all()
        )
        materias = [
            _materia_from_inscripcion(inscripcion)
            for inscripcion in inscripciones
        ]
        return {
            "materias": materias,
            "total": len(materias),
            "error_code": "",
            "message": "Materias obtenidas",
        }
    except Exception as exc:
        logger.exception("Error en get_materias_by_alumno_handler")
        return {
            "materias": [],
            "total": 0,
            "error_code": "INTERNAL_ERROR",
            "message": str(exc),
        }
    finally:
        db.close()


async def get_alumno_by_id_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    alumno_id = payload.get("alumno_id")
    if not alumno_id:
        return {
            "found": False,
            "alumno": None,
            "error_code": "MISSING_ALUMNO_ID",
            "message": "alumno_id es requerido",
        }

    db = SessionLocal()
    try:
        alumno = db.query(Alumno).filter(Alumno.alumno_id == alumno_id).first()
        if not alumno:
            return {
                "found": False,
                "alumno": None,
                "error_code": "ALUMNO_NOT_FOUND",
                "message": "Alumno no encontrado",
            }
        return {
            "found": True,
            "alumno": _alumno_to_dict(alumno),
            "error_code": "",
            "message": "Alumno encontrado",
        }
    except Exception as exc:
        logger.exception("Error en get_alumno_by_id_handler")
        return {
            "found": False,
            "alumno": None,
            "error_code": "INTERNAL_ERROR",
            "message": str(exc),
        }
    finally:
        db.close()


async def get_docente_by_id_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    docente_id = payload.get("docente_id")
    if not docente_id:
        return {
            "found": False,
            "docente": None,
            "error_code": "MISSING_DOCENTE_ID",
            "message": "docente_id es requerido",
        }

    db = SessionLocal()
    try:
        docente = db.query(Docente).filter(Docente.docente_id == docente_id).first()
        if not docente:
            return {
                "found": False,
                "docente": None,
                "error_code": "DOCENTE_NOT_FOUND",
                "message": "Docente no encontrado",
            }
        return {
            "found": True,
            "docente": _docente_to_dict(docente),
            "error_code": "",
            "message": "Docente encontrado",
        }
    except Exception as exc:
        logger.exception("Error en get_docente_by_id_handler")
        return {
            "found": False,
            "docente": None,
            "error_code": "INTERNAL_ERROR",
            "message": str(exc),
        }
    finally:
        db.close()


async def get_docente_by_nombre_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    nombre = payload.get("nombre") or payload.get("nombre_completo")
    if not nombre:
        return {
            "found": False,
            "docente": None,
            "error_code": "MISSING_NOMBRE",
            "message": "nombre es requerido",
        }

    db = SessionLocal()
    try:
        palabras_buscadas = set(_normalizar(nombre).split())
        docentes = (
            db.query(Docente)
            .filter(Docente.estatus_laboral == True)
            .all()
        )

        for docente in docentes:
            palabras_docente = set(_normalizar(docente.nombre_completo).split())
            if palabras_buscadas.issubset(palabras_docente):
                return {
                    "found": True,
                    "docente": _docente_to_dict(docente),
                    "error_code": "",
                    "message": "Docente encontrado",
                }

        return {
            "found": False,
            "docente": None,
            "error_code": "DOCENTE_NOT_FOUND",
            "message": "Docente no encontrado",
        }
    except Exception as exc:
        logger.exception("Error en get_docente_by_nombre_handler")
        return {
            "found": False,
            "docente": None,
            "error_code": "INTERNAL_ERROR",
            "message": str(exc),
        }
    finally:
        db.close()


async def get_docente_by_email_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    email = payload.get("email") or payload.get("correo")
    if not email:
        return {
            "found": False,
            "docente": None,
            "error_code": "MISSING_EMAIL",
            "message": "email es requerido",
        }

    db = SessionLocal()
    try:
        docente = (
            db.query(Docente)
            .filter(Docente.correo == email.strip().lower())
            .first()
        )
        if not docente:
            return {
                "found": False,
                "docente": None,
                "error_code": "DOCENTE_NOT_FOUND",
                "message": "Docente no encontrado",
            }
        return {
            "found": True,
            "docente": _docente_to_dict(docente),
            "error_code": "",
            "message": "Docente encontrado",
        }
    except Exception as exc:
        logger.exception("Error en get_docente_by_email_handler")
        return {
            "found": False,
            "docente": None,
            "error_code": "INTERNAL_ERROR",
            "message": str(exc),
        }
    finally:
        db.close()


async def get_alumno_by_email_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    email = payload.get("email") or payload.get("correo")
    if not email:
        return {
            "found": False,
            "alumno": None,
            "error_code": "MISSING_EMAIL",
            "message": "email es requerido",
        }

    db = SessionLocal()
    try:
        alumno = (
            db.query(Alumno)
            .filter(Alumno.correo == email.strip().lower())
            .first()
        )
        if not alumno:
            return {
                "found": False,
                "alumno": None,
                "error_code": "ALUMNO_NOT_FOUND",
                "message": "Alumno no encontrado",
            }
        return {
            "found": True,
            "alumno": _alumno_to_dict(alumno),
            "error_code": "",
            "message": "Alumno encontrado",
        }
    except Exception as exc:
        logger.exception("Error en get_alumno_by_email_handler")
        return {
            "found": False,
            "alumno": None,
            "error_code": "INTERNAL_ERROR",
            "message": str(exc),
        }
    finally:
        db.close()
