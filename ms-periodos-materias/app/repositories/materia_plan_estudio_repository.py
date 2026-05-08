from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.materia_plan_estudio import MateriaPlanEstudio


class MateriaPlanEstudioRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list(
        self,
        materia_catalogo_id: UUID | None = None,
        plan_estudio_id: UUID | None = None,
        activa: bool | None = None,
    ) -> list[MateriaPlanEstudio]:
        query = select(MateriaPlanEstudio)

        if materia_catalogo_id is not None:
            query = query.where(
                MateriaPlanEstudio.materia_catalogo_id == materia_catalogo_id
            )

        if plan_estudio_id is not None:
            query = query.where(MateriaPlanEstudio.plan_estudio_id == plan_estudio_id)

        if activa is not None:
            query = query.where(MateriaPlanEstudio.activa.is_(activa))

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(
        self,
        materia_plan_estudio_id: UUID,
    ) -> MateriaPlanEstudio | None:
        result = await self.db.execute(
            select(MateriaPlanEstudio).where(
                MateriaPlanEstudio.materia_plan_estudio_id == materia_plan_estudio_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_materia_and_plan(
        self,
        materia_catalogo_id: UUID,
        plan_estudio_id: UUID,
    ) -> MateriaPlanEstudio | None:
        result = await self.db.execute(
            select(MateriaPlanEstudio).where(
                MateriaPlanEstudio.materia_catalogo_id == materia_catalogo_id,
                MateriaPlanEstudio.plan_estudio_id == plan_estudio_id,
            )
        )
        return result.scalar_one_or_none()

    async def create(self, data: dict) -> MateriaPlanEstudio:
        relation = MateriaPlanEstudio(**data)

        self.db.add(relation)
        await self.db.commit()
        await self.db.refresh(relation)

        return relation

    async def update(
        self,
        relation: MateriaPlanEstudio,
        data: dict,
    ) -> MateriaPlanEstudio:
        for field, value in data.items():
            setattr(relation, field, value)

        await self.db.commit()
        await self.db.refresh(relation)

        return relation

    async def deactivate(self, relation: MateriaPlanEstudio) -> MateriaPlanEstudio:
        relation.activa = False

        await self.db.commit()
        await self.db.refresh(relation)

        return relation