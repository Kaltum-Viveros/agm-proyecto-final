from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.plan_estudio import PlanEstudio
from app.db.pagination import paginate_query


class PlanEstudioRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list(
        self,
        activo: bool | None = None,
        page: int = 1,
        limit: int = 10,
    ):
        stmt = select(PlanEstudio).order_by(PlanEstudio.nombre.asc())

        if activo is not None:
            stmt = stmt.where(PlanEstudio.activo == activo)

        return await paginate_query(
            db=self.db,
            stmt=stmt,
            page=page,
            limit=limit,
        )

    async def get_by_id(self, plan_estudio_id: UUID) -> PlanEstudio | None:
        result = await self.db.execute(
            select(PlanEstudio).where(PlanEstudio.plan_estudio_id == plan_estudio_id)
        )
        return result.scalar_one_or_none()

    async def get_by_nombre(self, nombre: str) -> PlanEstudio | None:
        result = await self.db.execute(
            select(PlanEstudio).where(PlanEstudio.nombre == nombre)
        )
        return result.scalar_one_or_none()

    async def create(self, data: dict) -> PlanEstudio:
        plan_estudio = PlanEstudio(**data)

        self.db.add(plan_estudio)
        await self.db.commit()
        await self.db.refresh(plan_estudio)

        return plan_estudio

    async def update(self, plan_estudio: PlanEstudio, data: dict) -> PlanEstudio:
        for field, value in data.items():
            setattr(plan_estudio, field, value)

        await self.db.commit()
        await self.db.refresh(plan_estudio)

        return plan_estudio

    async def deactivate(self, plan_estudio: PlanEstudio) -> PlanEstudio:
        plan_estudio.activo = False

        await self.db.commit()
        await self.db.refresh(plan_estudio)

        return plan_estudio