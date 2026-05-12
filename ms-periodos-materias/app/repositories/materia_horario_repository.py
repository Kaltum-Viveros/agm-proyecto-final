from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.materia_horario import MateriaHorario
from app.db.pagination import paginate_query


class MateriaHorarioRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list(
        self,
        materia_ofertada_id: UUID | None = None,
        dia: str | None = None,
        page: int = 1,
        limit: int = 10,
    ):
        stmt = select(MateriaHorario).order_by(
            MateriaHorario.dia.asc(),
            MateriaHorario.hora_inicio.asc(),
        )

        if materia_ofertada_id is not None:
            stmt = stmt.where(
                MateriaHorario.materia_ofertada_id == materia_ofertada_id
            )

        if dia:
            stmt = stmt.where(MateriaHorario.dia == dia)

        return await paginate_query(
            db=self.db,
            stmt=stmt,
            page=page,
            limit=limit,
        )

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