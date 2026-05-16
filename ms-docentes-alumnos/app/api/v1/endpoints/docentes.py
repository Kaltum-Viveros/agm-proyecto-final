from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.schemas.docente import DocenteCreate, DocenteOut, DocenteUpdate
from app.repositories.docente_repository import docente_repository
from app.db.session import get_db
from app.api.deps import role_required, get_current_user

router = APIRouter()

# 1. Crear un Docente
@router.post("/", response_model=DocenteOut, status_code=status.HTTP_201_CREATED)
def create_docente(
    docente_in: DocenteCreate, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(role_required("Administrador"))
):
    # Verificamos si el correo ya existe
    existing = docente_repository.get_by_email(db, email=docente_in.correo)
    if existing:
        raise HTTPException(
            status_code=400,
            detail="El correo ya está registrado en el sistema de docentes."
        )
    # Si no existe, lo creamos pasando el diccionario de datos
    return docente_repository.create(db, obj_in=docente_in.model_dump())

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