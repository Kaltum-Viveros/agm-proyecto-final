from sqlalchemy.orm import Session
from app.models.alumno import Alumno
from app.repositories.base import BaseRepository
from uuid import UUID

class AlumnoRepository(BaseRepository[Alumno]):
    # Método para el proceso de importación del PDF
    def create_or_update(self, db: Session, alumno_data: dict) -> Alumno:
        # Buscamos si el alumno ya existe por su matrícula
        db_alumno = self.get_by_matricula(db, alumno_data["matricula"])

        if db_alumno:
            # Si existe, actualizamos sus campos PERO nunca sobrescribimos user_id
            # con un valor vacío o generado localmente.
            for key, value in alumno_data.items():
                if key == "user_id":
                    # Solo actualizar user_id si se provee uno real y no vacío.
                    if value:
                        setattr(db_alumno, key, value)
                else:
                    setattr(db_alumno, key, value)
        else:
            # Si no existe, lo creamos. user_id debe provenir de MS-1 (obligatorio).
            if not alumno_data.get("user_id"):
                raise ValueError(
                    "No se puede crear un alumno sin user_id. "
                    "El user_id debe provenir de MS-1 vía gRPC."
                )
            db_alumno = Alumno(**alumno_data)
            db.add(db_alumno)

        db.commit()
        db.refresh(db_alumno)
        return db_alumno

    def create(self, db: Session, *, obj_in: dict) -> Alumno:
        if not obj_in.get("user_id"):
            raise ValueError(
                "No se puede crear un alumno sin user_id. "
                "El user_id debe provenir de MS-1 vía gRPC."
            )
        db_obj = Alumno(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_matricula(self, db: Session, matricula: str) -> Alumno:
        return db.query(Alumno).filter(Alumno.matricula == matricula).first()

    def get_by_materia(self, db: Session, materia_id: UUID):
        from app.models.inscripcion import Inscripcion
        return db.query(Alumno).join(Inscripcion).filter(
            Inscripcion.materia_id == materia_id,
            Inscripcion.activa == True
        ).all()

# IMPORTANTE: Esta es la instancia que busca app/api/v1/endpoints/alumnos.py
alumno_repository = AlumnoRepository(Alumno)