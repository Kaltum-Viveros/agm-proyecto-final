from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.materia_catalogo_repository import MateriaCatalogoRepository
from app.repositories.materia_plan_estudio_repository import (
    MateriaPlanEstudioRepository,
)
from app.repositories.plan_estudio_repository import PlanEstudioRepository
from app.schemas.materia_plan_estudio import (
    MateriaPlanEstudioCreate,
    MateriaPlanEstudioUpdate,
)


class MateriaPlanEstudioService:
    def __init__(self, db: AsyncSession):
        self.repository = MateriaPlanEstudioRepository(db)
        self.materia_repository = MateriaCatalogoRepository(db)
        self.plan_repository = PlanEstudioRepository(db)

    async def list_relaciones(
        self,
        materia_catalogo_id: UUID | None = None,
        plan_estudio_id: UUID | None = None,
        activa: bool | None = None,
    ):
        return await self.repository.list(
            materia_catalogo_id=materia_catalogo_id,
            plan_estudio_id=plan_estudio_id,
            activa=activa,
        )

    async def get_relacion(self, materia_plan_estudio_id: UUID):
        relation = await self.repository.get_by_id(materia_plan_estudio_id)

        if relation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Relación materia-plan de estudio no encontrada",
            )

        return relation

    async def create_relacion(self, payload: MateriaPlanEstudioCreate):
        materia = await self.materia_repository.get_by_id(payload.materia_catalogo_id)

        if materia is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Materia del catálogo no encontrada",
            )

        plan = await self.plan_repository.get_by_id(payload.plan_estudio_id)

        if plan is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan de estudio no encontrado",
            )

        existing = await self.repository.get_by_materia_and_plan(
            materia_catalogo_id=payload.materia_catalogo_id,
            plan_estudio_id=payload.plan_estudio_id,
        )

        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="La materia ya está asociada a ese plan de estudio",
            )

        return await self.repository.create(payload.model_dump())

    async def update_relacion(
        self,
        materia_plan_estudio_id: UUID,
        payload: MateriaPlanEstudioUpdate,
    ):
        relation = await self.get_relacion(materia_plan_estudio_id)
        data = payload.model_dump(exclude_unset=True)

        return await self.repository.update(relation, data)

    async def deactivate_relacion(self, materia_plan_estudio_id: UUID):
        relation = await self.get_relacion(materia_plan_estudio_id)

        return await self.repository.deactivate(relation)