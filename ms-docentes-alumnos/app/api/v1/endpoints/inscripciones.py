from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.schemas.inscripcion import InscripcionCreate, InscripcionOut
from app.repositories.inscripcion_repository import inscripcion_repository
from app.repositories.docente_repository import docente_repository
from app.repositories.alumno_repository import alumno_repository
from app.db.session import get_db
from app.api.deps import role_required, get_current_user

router = APIRouter()

@router.post("/", response_model=InscripcionOut, status_code=status.HTTP_201_CREATED)
def crear_inscripcion(
    ins_in: InscripcionCreate, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(role_required("Administrador", "Docente"))
):
    # 1. Validar que el docente exista
    if not docente_repository.get(db, id=ins_in.docente_id):
        raise HTTPException(status_code=404, detail="Docente no encontrado")
    
    # 2. Validar que el alumno exista
    if not alumno_repository.get(db, id=ins_in.alumno_id):
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
        
    # 3. Validar que no exista ya esa inscripción
    if inscripcion_repository.get_by_relacion(db, ins_in.docente_id, ins_in.alumno_id):
        raise HTTPException(status_code=400, detail="El alumno ya está inscrito con este docente")

    return inscripcion_repository.create(db, obj_in=ins_in.model_dump())

@router.get("/", response_model=List[InscripcionOut])
def listar_inscripciones(
    alumno_id: Optional[UUID] = None,
    docente_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(role_required("Administrador", "Docente", "Alumno"))
):
    return inscripcion_repository.get_filtrado(db, alumno_id=alumno_id, docente_id=docente_id)