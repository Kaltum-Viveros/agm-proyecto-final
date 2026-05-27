import grpc
import logging
import asyncio
import os
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.schemas.alumno import AlumnoCreate, AlumnoOut, AlumnoUpdate
from uuid import UUID
from app.repositories.inscripcion_repository import inscripcion_repository
from app.repositories.alumno_repository import alumno_repository
from app.db.session import get_db
from app.api.deps import role_required, get_current_user
from app.messaging.clients.auth_hybrid_client import auth_client
from app.messaging.clients.notificaciones_event_client import notificaciones_event_client
from app.grpc.clients.notif_client import NotifClient

logger = logging.getLogger(__name__)

router = APIRouter()
notif_client = NotifClient()


async def _enviar_bienvenida_alumno(
    alumno_id: str,
    materia_id: str,
    password_temporal: str,
) -> None:
    mode = os.getenv("COMMUNICATION_MODE", "hybrid").lower()

    if mode == "grpc":
        notif_client.enviar_bienvenida(alumno_id, materia_id, password_temporal)
        return

    try:
        await notificaciones_event_client.publish_bienvenida_alumno(
            alumno_id=alumno_id,
            materia_id=materia_id,
            password_temporal=password_temporal,
        )
        return
    except Exception as exc:
        logger.warning(
            "[NotificacionesEventClient] RabbitMQ event publish failed, "
            "falling back to gRPC: %s",
            exc,
        )

    if mode != "rabbit":
        notif_client.enviar_bienvenida(alumno_id, materia_id, password_temporal)


def _enviar_baja_alumno(
    alumno_id: str,
    docente_id: str,
    materia_id: str,
) -> None:
    mode = os.getenv("COMMUNICATION_MODE", "hybrid").lower()

    if mode == "grpc":
        notif_client.enviar_baja(alumno_id, docente_id, materia_id)
        return

    try:
        asyncio.run(
            notificaciones_event_client.publish_baja_alumno(
                alumno_id=alumno_id,
                docente_id=docente_id,
                materia_id=materia_id,
            )
        )
        return
    except Exception as exc:
        logger.warning(
            "[NotificacionesEventClient] RabbitMQ event publish failed, "
            "falling back to gRPC: %s",
            exc,
        )

    if mode != "rabbit":
        notif_client.enviar_baja(alumno_id, docente_id, materia_id)

@router.post("/", response_model=AlumnoOut, status_code=status.HTTP_201_CREATED)
async def create_alumno(
    alumno_in: AlumnoCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(role_required("Administrador"))
):
    existing = alumno_repository.get_by_matricula(db, matricula=alumno_in.matricula)
    if existing:
        raise HTTPException(status_code=409, detail="La matrícula ya está registrada.")

    # 1. Crear identidad en MS-1 vía gRPC ANTES de guardar localmente.
    try:
        u_id, temp_pass = await auth_client.create_or_get_user_identity(
            nombre=alumno_in.nombre_completo,
            email=alumno_in.correo,
            role="Alumno"
        )
    except grpc.RpcError as e:
        logger.error(
            f"[MS-3][Alumno][Creación manual] Fallo de conexión con MS-1. "
            f"correo={alumno_in.correo} error={e.details()}"
        )
        raise HTTPException(
            status_code=503,
            detail="El servicio de autenticación (MS-1) no está disponible. Intenta más tarde."
        )

    if not u_id:
        logger.error(
            f"[MS-3][Alumno][Creación manual] MS-1 no devolvió user_id. "
            f"correo={alumno_in.correo}"
        )
        raise HTTPException(
            status_code=400,
            detail="No se pudo crear o reutilizar la identidad en el servicio de autenticación."
        )

    # 2. Guardar en MS-3 con el user_id real de MS-1.
    alumno_data = alumno_in.model_dump()
    alumno_data["user_id"] = u_id
    nuevo_alumno = alumno_repository.create(db, obj_in=alumno_data)

    # 3. Enviar notificación de bienvenida (MS-6).
    #    Solo si MS-1 devolvió contraseña temporal; no inventamos una local.
    if temp_pass:
        try:
            await _enviar_bienvenida_alumno(
                alumno_id=str(nuevo_alumno.alumno_id),
                materia_id="",
                password_temporal=temp_pass,
            )
        except Exception as notif_err:
            logger.warning(
                f"[MS-3][Alumno][Creación manual] No se pudo enviar notificación. "
                f"correo={alumno_in.correo} error={notif_err}"
            )

    return nuevo_alumno

@router.get("/", response_model=List[AlumnoOut])
def read_alumnos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return alumno_repository.get_multi(db, skip=skip, limit=limit)

@router.get("/materia/{materia_id}", response_model=List[AlumnoOut])
def read_alumnos_by_materia(
    materia_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return alumno_repository.get_by_materia(db, materia_id=materia_id)

@router.get("/{alumno_id}", response_model=AlumnoOut)
def read_alumno(
    alumno_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    alumno = alumno_repository.get(db, id=alumno_id)
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    return alumno

@router.put("/{alumno_id}", response_model=AlumnoOut)
def update_alumno(
    alumno_id: UUID,
    alumno_in: AlumnoUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(role_required("Administrador"))
):
    alumno = alumno_repository.get(db, id=alumno_id)
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")

    update_data = alumno_in.model_dump(exclude_unset=True)
    return alumno_repository.update(db, db_obj=alumno, obj_in=update_data)

@router.delete("/{alumno_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alumno(
    alumno_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(role_required("Administrador"))
):
    alumno = alumno_repository.get(db, id=alumno_id)
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")

    alumno_repository.remove(db, id=alumno_id)
    return None

@router.delete("/{alumno_id}/baja", status_code=status.HTTP_204_NO_CONTENT)
def baja_alumno(
    alumno_id: UUID,
    materia_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(role_required("Alumno"))
):
    inscripcion = inscripcion_repository.get_by_materia_and_alumno(db, materia_id=materia_id, alumno_id=alumno_id)
    if not inscripcion:
        raise HTTPException(status_code=404, detail="Inscripción no encontrada o ya dada de baja")

    # Baja lógica
    inscripcion_repository.update(db, db_obj=inscripcion, obj_in={"activa": False})

    # Notificar al docente vía MS-6
    try:
        _enviar_baja_alumno(
            alumno_id=str(alumno_id),
            docente_id=str(inscripcion.docente_id),
            materia_id=str(materia_id)
        )
    except Exception as notif_err:
        logger.warning(
            f"[MS-3][Alumno][Baja] No se pudo enviar notificación de baja. "
            f"alumno_id={alumno_id} error={notif_err}"
        )

    return None
