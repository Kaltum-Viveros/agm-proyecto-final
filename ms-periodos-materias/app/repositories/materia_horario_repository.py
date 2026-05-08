from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.materia_horario import MateriaHorario


class MateriaHorarioRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list(
        self,
        materia_ofertada_id: UUID | None = None,
    ) -> list[MateriaHorario]:
        query = select(MateriaHorario).order_by(
            MateriaHorario.dia.asc(),
            MateriaHorario.hora_inicio.asc(),
        )

        if materia_ofertada_id is not None:
            query = query.where(
                MateriaHorario.materia_ofertada_id == materia_ofertada_id
            )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, materia_horario_id: UUID) -> MateriaHorario | None:
        result = await self.db.execute(
            select(MateriaHorario).where(
                MateriaHorario.materia_horario_id == materia_horario_id
            )
        )
        return result.scalar_one_or_none()

    async def create(self, data: dict) -> MateriaHorario:
        horario = MateriaHorario(**data)

        self.db.add(horario)
        await self.db.commit()
        await self.db.refresh(horario)

        return horario

    async def update(self, horario: MateriaHorario, data: dict) -> MateriaHorario:
        for field, value in data.items():
            setattr(horario, field, value)

        await self.db.commit()
        await self.db.refresh(horario)

        return horario

    async def delete(self, horario: MateriaHorario) -> None:
        await self.db.delete(horario)
        await self.db.commit()