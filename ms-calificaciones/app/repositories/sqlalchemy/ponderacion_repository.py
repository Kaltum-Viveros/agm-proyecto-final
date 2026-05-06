from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.ponderacion import Ponderacion


class PonderacionRepository:
    def __init__(self, db: Session):
        self.db = db

    def _to_dict(self, ponderacion: Ponderacion) -> dict:
        return {
            "id": ponderacion.id,
            "materia_id": ponderacion.materia_id,
            "nombre": ponderacion.nombre,
            "porcentaje": ponderacion.porcentaje,
            "orden": ponderacion.orden,
        }

    def get_by_materia(self, materia_id: UUID) -> list[dict]:
        stmt = (
            select(Ponderacion)
            .where(Ponderacion.materia_id == materia_id)
            .order_by(Ponderacion.orden.asc())
        )

        ponderaciones = self.db.scalars(stmt).all()

        return [self._to_dict(ponderacion) for ponderacion in ponderaciones]

    def replace_by_materia(self, materia_id: UUID, criterios: list[dict]) -> list[dict]:
        self.db.execute(
            delete(Ponderacion).where(Ponderacion.materia_id == materia_id)
        )

        nuevas_ponderaciones = [
            Ponderacion(
                id=criterio["id"],
                materia_id=criterio["materia_id"],
                nombre=criterio["nombre"],
                porcentaje=criterio["porcentaje"],
                orden=criterio["orden"],
            )
            for criterio in criterios
        ]

        self.db.add_all(nuevas_ponderaciones)
        self.db.commit()

        for ponderacion in nuevas_ponderaciones:
            self.db.refresh(ponderacion)

        return [self._to_dict(ponderacion) for ponderacion in nuevas_ponderaciones]

    def exists_for_materia(self, materia_id: UUID) -> bool:
        stmt = select(Ponderacion.id).where(Ponderacion.materia_id == materia_id)
        return self.db.scalar(stmt) is not None

    def delete_by_materia(self, materia_id: UUID) -> bool:
        ponderaciones = self.get_by_materia(materia_id)

        if not ponderaciones:
            return False

        self.db.execute(
            delete(Ponderacion).where(Ponderacion.materia_id == materia_id)
        )
        self.db.commit()

        return True

    def get_ids_by_materia(self, materia_id: UUID) -> list[UUID]:
        stmt = select(Ponderacion.id).where(Ponderacion.materia_id == materia_id)
        return list(self.db.scalars(stmt).all())