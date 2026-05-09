from sqlalchemy.orm import Session
from app.models.inscripcion import Inscripcion
from app.repositories.base import BaseRepository

class InscripcionRepository(BaseRepository[Inscripcion]):
    def create(self, db: Session, *, obj_in: dict) -> Inscripcion:
        db_obj = Inscripcion(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_relacion(self, db: Session, docente_id: UUID, alumno_id: UUID):
        # Evita que un alumno se inscriba dos veces con el mismo docente
        return db.query(Inscripcion).filter(
            Inscripcion.docente_id == docente_id,
            Inscripcion.alumno_id == alumno_id
        ).first()

inscripcion_repository = InscripcionRepository(Inscripcion)