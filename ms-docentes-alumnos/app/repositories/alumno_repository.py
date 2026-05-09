from sqlalchemy.orm import Session
from app.models.alumno import Alumno
from app.repositories.base import BaseRepository
from uuid import UUID

class AlumnoRepository(BaseRepository[Alumno]):
    def create(self, db: Session, *, obj_in: dict) -> Alumno:
        db_obj = Alumno(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_matricula(self, db: Session, matricula: str) -> Alumno:
        return db.query(Alumno).filter(Alumno.matricula == matricula).first()

alumno_repository = AlumnoRepository(Alumno)