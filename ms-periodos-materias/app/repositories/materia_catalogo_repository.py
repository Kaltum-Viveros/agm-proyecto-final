from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.materia_catalogo import MateriaCatalogo
from app.db.pagination import paginate_query


class MateriaCatalogoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list(
        self,
        activo: bool | None = None,
        clave: str | None = None,
        page: int = 1,
        limit: int = 10,
    ):
        stmt = select(MateriaCatalogo).order_by(MateriaCatalogo.nombre.asc())

        if activo is not None:
            stmt = stmt.where(MateriaCatalogo.activo == activo)

        if clave:
            stmt = stmt.where(MateriaCatalogo.clave.ilike(f"%{clave}%"))

        return await paginate_query(
            db=self.db,
            stmt=stmt,
            page=page,
            limit=limit,
        )

    async def get_by_id(self, materia_catalogo_id: UUID) -> MateriaCatalogo | None:
        result = await self.db.execute(
            select(MateriaCatalogo).where(
                MateriaCatalogo.materia_catalogo_id == materia_catalogo_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_clave(self, clave: str) -> MateriaCatalogo | None:
        result = await self.db.execute(
            select(MateriaCatalogo).where(MateriaCatalogo.clave == clave)
        )
        return result.scalar_one_or_none()

    async def create(self, data: dict) -> MateriaCatalogo:
        materia = MateriaCatalogo(**data)

        self.db.add(materia)
        await self.db.commit()
        await self.db.refresh(materia)

        return materia

    async def update(self, materia: MateriaCatalogo, data: dict) -> MateriaCatalogo:
        for field, value in data.items():
            setattr(materia, field, value)

        await self.db.commit()
        await self.db.refresh(materia)

        return materia

    async def deactivate(self, materia: MateriaCatalogo) -> MateriaCatalogo:
        materia.activo = False

        await self.db.commit()
        await self.db.refresh(materia)

        return materia