from sqlalchemy.orm import Session
from app.models.docente import Docente
from app.repositories.base import BaseRepository
from uuid import UUID

class DocenteRepository(BaseRepository[Docente]):
    def create(self, db: Session, *, obj_in: dict) -> Docente:
        db_obj = Docente(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_email(self, db: Session, email: str) -> Docente:
        return db.query(Docente).filter(Docente.correo == email).first()

docente_repository = DocenteRepository(Docente)