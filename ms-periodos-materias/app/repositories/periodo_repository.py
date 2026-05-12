from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.periodo import Periodo
from app.db.pagination import paginate_query

class PeriodoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list(
        self,
        activo: bool | None = None,
        page: int = 1,
        limit: int = 10,
    ):
        stmt = select(Periodo).order_by(Periodo.fecha_inicio.desc())

        if activo is not None:
            stmt = stmt.where(Periodo.activo == activo)

        return await paginate_query(
            db=self.db,
            stmt=stmt,
            page=page,
            limit=limit,
        )

    async def get_by_id(self, periodo_id: UUID) -> Periodo | None:
        result = await self.db.execute(
            select(Periodo).where(Periodo.periodo_id == periodo_id)
        )
        return result.scalar_one_or_none()

    async def deactivate_all_active(self) -> None:
        await self.db.execute(
            update(Periodo)
            .where(Periodo.activo.is_(True))
            .values(activo=False)
        )
        await self.db.commit()

    async def create(self, data: dict) -> Periodo:
        periodo = Periodo(**data)

        self.db.add(periodo)
        await self.db.commit()
        await self.db.refresh(periodo)

        return periodo

    async def update(self, periodo: Periodo, data: dict) -> Periodo:
        for field, value in data.items():
            setattr(periodo, field, value)

        await self.db.commit()
        await self.db.refresh(periodo)

        return periodo

    async def deactivate(self, periodo: Periodo) -> Periodo:
        periodo.activo = False

        await self.db.commit()
        await self.db.refresh(periodo)

        return periodo