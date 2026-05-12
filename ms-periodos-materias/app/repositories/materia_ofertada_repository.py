from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.materia_ofertada import MateriaOfertada
from app.db.pagination import paginate_query


class MateriaOfertadaRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list(
        self,
        periodo_id: UUID | None = None,
        materia_catalogo_id: UUID | None = None,
        docente_id: UUID | None = None,
        estado: str | None = None,
        nrc: str | None = None,
        page: int = 1,
        limit: int = 10,
    ):
        stmt = select(MateriaOfertada).order_by(MateriaOfertada.nrc.asc())

        if periodo_id is not None:
            stmt = stmt.where(MateriaOfertada.periodo_id == periodo_id)

        if materia_catalogo_id is not None:
            stmt = stmt.where(
                MateriaOfertada.materia_catalogo_id == materia_catalogo_id
            )

        if docente_id is not None:
            stmt = stmt.where(MateriaOfertada.docente_id == docente_id)

        if estado:
            stmt = stmt.where(MateriaOfertada.estado == estado)

        if nrc:
            stmt = stmt.where(MateriaOfertada.nrc.ilike(f"%{nrc}%"))

        return await paginate_query(
            db=self.db,
            stmt=stmt,
            page=page,
            limit=limit,
        )

    async def get_by_id(self, materia_ofertada_id: UUID) -> MateriaOfertada | None:
        result = await self.db.execute(
            select(MateriaOfertada).where(
                MateriaOfertada.materia_ofertada_id == materia_ofertada_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_periodo_and_nrc(
        self,
        periodo_id: UUID,
        nrc: str,
    ) -> MateriaOfertada | None:
        result = await self.db.execute(
            select(MateriaOfertada).where(
                MateriaOfertada.periodo_id == periodo_id,
                MateriaOfertada.nrc == nrc,
            )
        )
        return result.scalar_one_or_none()

    async def create(self, data: dict) -> MateriaOfertada:
        materia_ofertada = MateriaOfertada(**data)

        self.db.add(materia_ofertada)
        await self.db.commit()
        await self.db.refresh(materia_ofertada)

        return materia_ofertada

    async def update(
        self,
        materia_ofertada: MateriaOfertada,
        data: dict,
    ) -> MateriaOfertada:
        for field, value in data.items():
            setattr(materia_ofertada, field, value)

        await self.db.commit()
        await self.db.refresh(materia_ofertada)

        return materia_ofertada

    async def deactivate(self, materia_ofertada: MateriaOfertada) -> MateriaOfertada:
        materia_ofertada.estado = "INACTIVA"

        await self.db.commit()
        await self.db.refresh(materia_ofertada)

        return materia_ofertada