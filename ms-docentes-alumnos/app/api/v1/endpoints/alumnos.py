from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.schemas.alumno import AlumnoCreate, AlumnoOut
from app.repositories.alumno_repository import alumno_repository
from app.db.session import get_db

router = APIRouter()

@router.post("/", response_model=AlumnoOut, status_code=status.HTTP_201_CREATED)
def create_alumno(alumno_in: AlumnoCreate, db: Session = Depends(get_db)):
    existing = alumno_repository.get_by_matricula(db, matricula=alumno_in.matricula)
    if existing:
        raise HTTPException(status_code=400, detail="La matrícula ya está registrada.")
    return alumno_repository.create(db, obj_in=alumno_in.model_dump())

@router.get("/", response_model=List[AlumnoOut])
def read_alumnos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return alumno_repository.get_multi(db, skip=skip, limit=limit)