from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.actividad import Actividad
from app.models.calificacion import Calificacion


class CalificacionRepository:
    def __init__(self, db: Session):
        self.db = db

    def _to_dict(self, calificacion: Calificacion) -> dict:
        actividad = calificacion.actividad

        return {
            "id": calificacion.id,
            "actividad_id": calificacion.actividad_id,
            "materia_id": actividad.materia_id if actividad else None,
            "alumno_id": calificacion.alumno_id,
            "calificacion": calificacion.calificacion,
            "observaciones": calificacion.observaciones,
            "actividad_nombre": actividad.nombre if actividad else None,
        }

    def create(self, calificacion: dict) -> dict:
        nueva_calificacion = Calificacion(
            id=calificacion["id"],
            actividad_id=calificacion["actividad_id"],
            alumno_id=calificacion["alumno_id"],
            calificacion=calificacion["calificacion"],
            observaciones=calificacion.get("observaciones"),
        )

        self.db.add(nueva_calificacion)
        self.db.commit()
        self.db.refresh(nueva_calificacion)

        stmt = (
            select(Calificacion)
            .options(joinedload(Calificacion.actividad))
            .where(Calificacion.id == nueva_calificacion.id)
        )

        nueva_calificacion = self.db.scalar(stmt)

        return self._to_dict(nueva_calificacion)

    def get_by_id(self, calificacion_id: UUID) -> dict | None:
        stmt = (
            select(Calificacion)
            .options(joinedload(Calificacion.actividad))
            .where(Calificacion.id == calificacion_id)
        )

        calificacion = self.db.scalar(stmt)

        if calificacion is None:
            return None

        return self._to_dict(calificacion)

    def get_by_actividad(self, actividad_id: UUID) -> list[dict]:
        stmt = (
            select(Calificacion)
            .options(joinedload(Calificacion.actividad))
            .where(Calificacion.actividad_id == actividad_id)
        )

        calificaciones = self.db.scalars(stmt).all()

        return [self._to_dict(calificacion) for calificacion in calificaciones]

    def get_by_materia(self, materia_id: UUID) -> list[dict]:
        stmt = (
            select(Calificacion)
            .join(Actividad, Calificacion.actividad_id == Actividad.id)
            .options(joinedload(Calificacion.actividad))
            .where(Actividad.materia_id == materia_id)
        )

        calificaciones = self.db.scalars(stmt).all()

        return [self._to_dict(calificacion) for calificacion in calificaciones]

    def get_by_alumno_and_materia(self, alumno_id: UUID, materia_id: UUID) -> list[dict]:
        stmt = (
            select(Calificacion)
            .join(Actividad, Calificacion.actividad_id == Actividad.id)
            .options(joinedload(Calificacion.actividad))
            .where(
                Calificacion.alumno_id == alumno_id,
                Actividad.materia_id == materia_id,
            )
        )

        calificaciones = self.db.scalars(stmt).all()

        return [self._to_dict(calificacion) for calificacion in calificaciones]

    def update(self, calificacion_id: UUID, data: dict) -> dict | None:
        calificacion = self.db.get(Calificacion, calificacion_id)

        if calificacion is None:
            return None

        campos_permitidos = {
            "calificacion",
            "observaciones",
        }

        for key, value in data.items():
            if key in campos_permitidos:
                setattr(calificacion, key, value)

        self.db.commit()
        self.db.refresh(calificacion)

        return self.get_by_id(calificacion_id)

    def delete(self, calificacion_id: UUID) -> bool:
        calificacion = self.db.get(Calificacion, calificacion_id)

        if calificacion is None:
            return False

        self.db.delete(calificacion)
        self.db.commit()

        return True

    def exists_by_actividad_and_alumno(
        self,
        actividad_id: UUID,
        alumno_id: UUID,
        exclude_calificacion_id: UUID | None = None,
    ) -> bool:
        stmt = select(Calificacion.id).where(
            Calificacion.actividad_id == actividad_id,
            Calificacion.alumno_id == alumno_id,
        )

        if exclude_calificacion_id is not None:
            stmt = stmt.where(Calificacion.id != exclude_calificacion_id)

        return self.db.scalar(stmt) is not None

    def exists_by_actividad_id(self, actividad_id: UUID) -> bool:
        stmt = (
            select(Calificacion.id)
            .where(Calificacion.actividad_id == actividad_id)
            .limit(1)
        )

        return self.db.scalar(stmt) is not None

    def get_by_actividad_and_alumno(
        self,
        actividad_id: UUID,
        alumno_id: UUID,
    ) -> dict | None:
        stmt = (
            select(Calificacion)
            .options(joinedload(Calificacion.actividad))
            .where(
                Calificacion.actividad_id == actividad_id,
                Calificacion.alumno_id == alumno_id,
            )
        )

        calificacion = self.db.scalar(stmt)

        if calificacion is None:
            return None

        return self._to_dict(calificacion)