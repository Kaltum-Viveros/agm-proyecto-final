from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.materia_catalogo_repository import MateriaCatalogoRepository
from app.schemas.materia_catalogo import MateriaCatalogoCreate, MateriaCatalogoUpdate


class MateriaCatalogoService:
    def __init__(self, db: AsyncSession):
        self.repository = MateriaCatalogoRepository(db)

    async def list_materias_catalogo(self, activo: bool | None = None):
        return await self.repository.list(activo=activo)

    async def get_materia_catalogo(self, materia_catalogo_id: UUID):
        materia = await self.repository.get_by_id(materia_catalogo_id)

        if materia is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Materia del catálogo no encontrada",
            )

        return materia

    async def create_materia_catalogo(self, payload: MateriaCatalogoCreate):
        existing = await self.repository.get_by_clave(payload.clave)

        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe una materia con esa clave",
            )

        return await self.repository.create(payload.model_dump())

    async def update_materia_catalogo(
        self,
        materia_catalogo_id: UUID,
        payload: MateriaCatalogoUpdate,
    ):
        materia = await self.get_materia_catalogo(materia_catalogo_id)
        data = payload.model_dump(exclude_unset=True)

        if "clave" in data:
            existing = await self.repository.get_by_clave(data["clave"])

            if existing is not None and existing.materia_catalogo_id != materia_catalogo_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Ya existe una materia con esa clave",
                )

        return await self.repository.update(materia, data)

    async def deactivate_materia_catalogo(self, materia_catalogo_id: UUID):
        materia = await self.get_materia_catalogo(materia_catalogo_id)

        return await self.repository.deactivate(materia)