from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.schemas.alumno import AlumnoCreate, AlumnoOut, AlumnoUpdate
from uuid import UUID
from app.repositories.inscripcion_repository import inscripcion_repository
from app.repositories.alumno_repository import alumno_repository
from app.db.session import get_db
from app.api.deps import role_required, get_current_user
from app.grpc.clients.auth_client import AuthClient
from app.grpc.clients.notif_client import NotifClient

router = APIRouter()
auth_client = AuthClient()
notif_client = NotifClient()

@router.post("/", response_model=AlumnoOut, status_code=status.HTTP_201_CREATED)
def create_alumno(
    alumno_in: AlumnoCreate, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(role_required("Administrador"))
):
    existing = alumno_repository.get_by_matricula(db, matricula=alumno_in.matricula)
    if existing:
        raise HTTPException(status_code=400, detail="La matrícula ya está registrada.")
    
    # 1. Crear identidad en MS-1
    u_id, temp_pass = auth_client.crear_identidad(
        nombre=alumno_in.nombre_completo,
        email=alumno_in.correo,
        role="Alumno"
    )
    if not u_id:
        raise HTTPException(status_code=500, detail="No se pudo crear la identidad en MS-Auth.")
    
    # 2. Guardar en MS-3
    alumno_data = alumno_in.model_dump()
    alumno_data["user_id"] = u_id
    nuevo_alumno = alumno_repository.create(db, obj_in=alumno_data)

    # 3. Enviar notificación de bienvenida (MS-6)
    notif_client.enviar_bienvenida(
        alumno_id=nuevo_alumno.alumno_id,
        materia_id="",
        password=temp_pass
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
    current_user: dict = Depends(role_required("Administrador"))
):
    inscripcion = inscripcion_repository.get_by_materia_and_alumno(db, materia_id=materia_id, alumno_id=alumno_id)
    if not inscripcion:
        raise HTTPException(status_code=404, detail="Inscripción no encontrada o ya dada de baja")
    
    # Baja lógica
    inscripcion_repository.update(db, db_obj=inscripcion, obj_in={"activa": False})
    
    # Notificar al docente vía MS-6
    notif_client.enviar_baja(
        alumno_id=str(alumno_id),
        docente_id=str(inscripcion.docente_id),
        materia_id=str(materia_id)
    )
    return None