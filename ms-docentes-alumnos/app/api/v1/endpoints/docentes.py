import grpc
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.schemas.docente import DocenteCreate, DocenteOut, DocenteUpdate
from app.repositories.docente_repository import docente_repository
from app.db.session import get_db
from app.api.deps import role_required, get_current_user
from app.grpc.clients.auth_client import AuthClient
from app.grpc.clients.notif_client import NotifClient

logger = logging.getLogger(__name__)

router = APIRouter()
auth_client = AuthClient()
notif_client = NotifClient()

# 1. Crear un Docente
@router.post("/", response_model=DocenteOut, status_code=status.HTTP_201_CREATED)
def create_docente(
    docente_in: DocenteCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(role_required("Administrador"))
):
    # Verificamos si el correo ya existe localmente
    existing = docente_repository.get_by_email(db, email=docente_in.correo)
    if existing:
        raise HTTPException(
            status_code=409,
            detail="El correo ya está registrado en el sistema de docentes."
        )

    # Crear o reutilizar identidad en MS-1 vía gRPC ANTES de guardar localmente.
    # grpc.RpcError se propaga si MS-1 no está disponible (error de red/timeout).
    try:
        user_id, temp_pass = auth_client.crear_identidad(
            nombre=docente_in.nombre_completo,
            email=docente_in.correo,
            role="Docente"
        )
    except grpc.RpcError as e:
        logger.error(
            f"[MS-3][Docente][Creación manual] Fallo de conexión con MS-1. "
            f"correo={docente_in.correo} error={e.details()}"
        )
        raise HTTPException(
            status_code=503,
            detail="El servicio de autenticación (MS-1) no está disponible. Intenta más tarde."
        )

    if not user_id:
        logger.error(
            f"[MS-3][Docente][Creación manual] MS-1 no devolvió user_id. "
            f"correo={docente_in.correo}"
        )
        raise HTTPException(
            status_code=400,
            detail="No se pudo crear o reutilizar la identidad en el servicio de autenticación."
        )

    # Guardamos el docente localmente con el user_id real de MS-1.
    docente_data = docente_in.model_dump()
    docente_data["user_id"] = user_id
    nuevo_docente = docente_repository.create(db, obj_in=docente_data)

    # Enviar notificación de bienvenida (MS-6) si se dispone de contraseña temporal.
    if temp_pass:
        try:
            notif_client.enviar_bienvenida(
                alumno_id=nuevo_docente.docente_id,
                materia_id="",
                password=temp_pass
            )
        except Exception as notif_err:
            # La falla en notificación no revierte la creación del docente.
            logger.warning(
                f"[MS-3][Docente][Creación manual] No se pudo enviar notificación. "
                f"correo={docente_in.correo} error={notif_err}"
            )

    return nuevo_docente

# 2. Listar todos los Docentes
@router.get("/", response_model=List[DocenteOut])
def read_docentes(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return docente_repository.get_multi(db, skip=skip, limit=limit)

# 3. Obtener Docente por ID
@router.get("/{docente_id}", response_model=DocenteOut)
def read_docente(
    docente_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    docente = docente_repository.get(db, id=docente_id)
    if not docente:
        raise HTTPException(status_code=404, detail="Docente no encontrado")
    return docente

# 4. Actualizar Docente
@router.put("/{docente_id}", response_model=DocenteOut)
def update_docente(
    docente_id: UUID,
    docente_in: DocenteUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(role_required("Administrador"))
):
    docente = docente_repository.get(db, id=docente_id)
    if not docente:
        raise HTTPException(status_code=404, detail="Docente no encontrado")

    update_data = docente_in.model_dump(exclude_unset=True)
    return docente_repository.update(db, db_obj=docente, obj_in=update_data)

# 5. Eliminar Docente
@router.delete("/{docente_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_docente(
    docente_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(role_required("Administrador"))
):
    docente = docente_repository.get(db, id=docente_id)
    if not docente:
        raise HTTPException(status_code=404, detail="Docente no encontrado")

    docente_repository.remove(db, id=docente_id)
    return None