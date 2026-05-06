from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models.actividad import Actividad


class ActividadRepository:
    def __init__(self, db: Session):
        self.db = db

    def _to_dict(self, actividad: Actividad) -> dict:
        return {
            "id": actividad.id,
            "materia_id": actividad.materia_id,
            "ponderacion_id": actividad.ponderacion_id,
            "nombre": actividad.nombre,
            "descripcion": actividad.descripcion,
            "valor_maximo": actividad.valor_maximo,
            "fecha_aplicacion": actividad.fecha_aplicacion,
            "estado": actividad.estado,
            "ponderacion_nombre": actividad.ponderacion.nombre if actividad.ponderacion else None,
        }

    def create(self, actividad: dict) -> dict:
        nueva_actividad = Actividad(
            id=actividad["id"],
            materia_id=actividad["materia_id"],
            ponderacion_id=actividad["ponderacion_id"],
            nombre=actividad["nombre"],
            descripcion=actividad.get("descripcion"),
            valor_maximo=actividad["valor_maximo"],
            fecha_aplicacion=actividad.get("fecha_aplicacion"),
            estado=actividad.get("estado", "activa"),
        )

        self.db.add(nueva_actividad)
        self.db.commit()
        self.db.refresh(nueva_actividad)

        return self._to_dict(nueva_actividad)

    def get_by_id(self, actividad_id: UUID) -> dict | None:
        stmt = (
            select(Actividad)
            .options(joinedload(Actividad.ponderacion))
            .where(Actividad.id == actividad_id)
        )

        actividad = self.db.scalar(stmt)

        if actividad is None:
            return None

        return self._to_dict(actividad)

    def get_by_materia(self, materia_id: UUID) -> list[dict]:
        stmt = (
            select(Actividad)
            .options(joinedload(Actividad.ponderacion))
            .where(Actividad.materia_id == materia_id)
            .order_by(
                Actividad.fecha_aplicacion.asc().nulls_last(),
                Actividad.nombre.asc(),
            )
        )

        actividades = self.db.scalars(stmt).all()

        return [self._to_dict(actividad) for actividad in actividades]

    def update(self, actividad_id: UUID, data: dict) -> dict | None:
        actividad = self.db.get(Actividad, actividad_id)

        if actividad is None:
            return None

        campos_permitidos = {
            "ponderacion_id",
            "nombre",
            "descripcion",
            "valor_maximo",
            "fecha_aplicacion",
            "estado",
        }

        for key, value in data.items():
            if key in campos_permitidos:
                setattr(actividad, key, value)

        self.db.commit()
        self.db.refresh(actividad)

        return self._to_dict(actividad)

    def delete(self, actividad_id: UUID) -> bool:
        actividad = self.db.get(Actividad, actividad_id)

        if actividad is None:
            return False

        self.db.delete(actividad)
        self.db.commit()

        return True

    def exists_by_ponderacion_ids(self, ponderacion_ids: list[UUID]) -> bool:
        if not ponderacion_ids:
            return False

        stmt = (
            select(Actividad.id)
            .where(Actividad.ponderacion_id.in_(ponderacion_ids))
            .limit(1)
        )

        return self.db.scalar(stmt) is not None

    def exists_by_ponderacion_and_nombre(
        self,
        ponderacion_id: UUID,
        nombre: str,
        exclude_actividad_id: UUID | None = None,
    ) -> bool:
        stmt = select(Actividad.id).where(
            Actividad.ponderacion_id == ponderacion_id,
            func.lower(Actividad.nombre) == nombre.lower().strip(),
        )

        if exclude_actividad_id is not None:
            stmt = stmt.where(Actividad.id != exclude_actividad_id)

        return self.db.scalar(stmt) is not None