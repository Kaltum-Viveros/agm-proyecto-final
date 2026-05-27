import asyncio
import logging
from contextlib import contextmanager
from typing import Any

from app.core.database import SessionLocal
from app.schemas.notificacion_schema import (
    BajaMateriaRequest,
    BienvenidaDocenteRequest,
    BienvenidaRequest,
    CierreMateriaRequest,
    ResetPasswordRequest,
)
from app.services import notificacion_service
from shared.agm_messaging.contracts import (
    EVENT_NOTIFICACIONES_BAJA_ALUMNO,
    EVENT_NOTIFICACIONES_BIENVENIDA_ALUMNO,
    EVENT_NOTIFICACIONES_BIENVENIDA_DOCENTE,
    EVENT_NOTIFICACIONES_CIERRE_MATERIA,
    EVENT_NOTIFICACIONES_RESET_PASSWORD,
)

logger = logging.getLogger(__name__)


@contextmanager
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def handle_bienvenida_alumno(payload: dict[str, Any]) -> None:
    logger.info("Evento recibido %s", EVENT_NOTIFICACIONES_BIENVENIDA_ALUMNO)
    print(f"Evento recibido {EVENT_NOTIFICACIONES_BIENVENIDA_ALUMNO}", flush=True)
    data = BienvenidaRequest(
        alumno_id=str(payload.get("alumno_id") or ""),
        materia_id=str(payload.get("materia_id") or ""),
        password_temporal=str(payload.get("password_temporal") or ""),
    )
    with db_session() as db:
        await asyncio.to_thread(notificacion_service.procesar_bienvenida, db, data)
    print(f"Evento procesado {EVENT_NOTIFICACIONES_BIENVENIDA_ALUMNO}", flush=True)


async def handle_bienvenida_docente(payload: dict[str, Any]) -> None:
    logger.info("Evento recibido %s", EVENT_NOTIFICACIONES_BIENVENIDA_DOCENTE)
    print(f"Evento recibido {EVENT_NOTIFICACIONES_BIENVENIDA_DOCENTE}", flush=True)
    data = BienvenidaDocenteRequest(
        docente_id=str(payload.get("docente_id") or ""),
        password_temporal=str(payload.get("password_temporal") or ""),
    )
    with db_session() as db:
        await asyncio.to_thread(notificacion_service.procesar_bienvenida_docente, db, data)
    print(f"Evento procesado {EVENT_NOTIFICACIONES_BIENVENIDA_DOCENTE}", flush=True)


async def handle_baja_alumno(payload: dict[str, Any]) -> None:
    logger.info("Evento recibido %s", EVENT_NOTIFICACIONES_BAJA_ALUMNO)
    print(f"Evento recibido {EVENT_NOTIFICACIONES_BAJA_ALUMNO}", flush=True)
    data = BajaMateriaRequest(
        alumno_id=str(payload.get("alumno_id") or ""),
        docente_id=str(payload.get("docente_id") or ""),
        materia_id=str(payload.get("materia_id") or ""),
    )
    with db_session() as db:
        await notificacion_service.procesar_baja_async(db, data)
    print(f"Evento procesado {EVENT_NOTIFICACIONES_BAJA_ALUMNO}", flush=True)


async def handle_cierre_materia(payload: dict[str, Any]) -> None:
    logger.info("Evento recibido %s", EVENT_NOTIFICACIONES_CIERRE_MATERIA)
    print(f"Evento recibido {EVENT_NOTIFICACIONES_CIERRE_MATERIA}", flush=True)
    data = CierreMateriaRequest(materia_id=str(payload.get("materia_id") or ""))
    with db_session() as db:
        await notificacion_service.procesar_cierre_materia_async(db, data)
    print(f"Evento procesado {EVENT_NOTIFICACIONES_CIERRE_MATERIA}", flush=True)


async def handle_reset_password(payload: dict[str, Any]) -> None:
    logger.info("Evento recibido %s", EVENT_NOTIFICACIONES_RESET_PASSWORD)
    print(f"Evento recibido {EVENT_NOTIFICACIONES_RESET_PASSWORD}", flush=True)
    data = ResetPasswordRequest(
        usuario_id=str(payload.get("usuario_id") or ""),
        email=str(payload.get("email") or ""),
        reset_token=str(payload.get("reset_token") or ""),
    )
    with db_session() as db:
        await asyncio.to_thread(notificacion_service.procesar_reset_password, db, data)
    print(f"Evento procesado {EVENT_NOTIFICACIONES_RESET_PASSWORD}", flush=True)


EVENT_HANDLERS = {
    EVENT_NOTIFICACIONES_BIENVENIDA_ALUMNO: handle_bienvenida_alumno,
    EVENT_NOTIFICACIONES_BIENVENIDA_DOCENTE: handle_bienvenida_docente,
    EVENT_NOTIFICACIONES_BAJA_ALUMNO: handle_baja_alumno,
    EVENT_NOTIFICACIONES_CIERRE_MATERIA: handle_cierre_materia,
    EVENT_NOTIFICACIONES_RESET_PASSWORD: handle_reset_password,
}
