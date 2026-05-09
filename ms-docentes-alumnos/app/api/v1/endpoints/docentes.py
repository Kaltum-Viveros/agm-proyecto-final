from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.schemas.docente import DocenteCreate, DocenteOut
from app.repositories.docente_repository import docente_repository
from app.db.session import get_db

router = APIRouter()

# 1. Crear un Docente
@router.post("/", response_model=DocenteOut, status_code=status.HTTP_201_CREATED)
def create_docente(docente_in: DocenteCreate, db: Session = Depends(get_db)):
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
def read_docentes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return docente_repository.get_multi(db, skip=skip, limit=limit)