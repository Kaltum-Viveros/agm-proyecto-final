from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.plan_estudio_repository import PlanEstudioRepository
from app.schemas.plan_estudio import PlanEstudioCreate, PlanEstudioUpdate


class PlanEstudioService:
    def __init__(self, db: AsyncSession):
        self.repository = PlanEstudioRepository(db)

    async def list_planes_estudio(
        self,
        activo: bool | None = None,
        page: int = 1,
        limit: int = 10,
    ):
        return await self.repository.list(
            activo=activo,
            page=page,
            limit=limit,
        )
    
    async def get_plan_estudio(self, plan_estudio_id: UUID):
        plan_estudio = await self.repository.get_by_id(plan_estudio_id)

        if plan_estudio is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan de estudio no encontrado",
            )

        return plan_estudio

    async def create_plan_estudio(self, payload: PlanEstudioCreate):
        existing = await self.repository.get_by_nombre(payload.nombre)

        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un plan de estudio con ese nombre",
            )

        return await self.repository.create(payload.model_dump())

    async def update_plan_estudio(self, plan_estudio_id: UUID, payload: PlanEstudioUpdate):
        plan_estudio = await self.get_plan_estudio(plan_estudio_id)
        data = payload.model_dump(exclude_unset=True)

        if "nombre" in data:
            existing = await self.repository.get_by_nombre(data["nombre"])

            if existing is not None and existing.plan_estudio_id != plan_estudio_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Ya existe un plan de estudio con ese nombre",
                )

        return await self.repository.update(plan_estudio, data)

    async def deactivate_plan_estudio(self, plan_estudio_id: UUID):
        plan_estudio = await self.get_plan_estudio(plan_estudio_id)

        return await self.repository.deactivate(plan_estudio)