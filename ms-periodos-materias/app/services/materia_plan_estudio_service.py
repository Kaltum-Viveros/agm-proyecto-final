from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.repositories.materia_catalogo_repository import MateriaCatalogoRepository
from app.repositories.materia_plan_estudio_repository import (
    MateriaPlanEstudioRepository,
)
from app.repositories.plan_estudio_repository import PlanEstudioRepository
from app.schemas.materia_plan_estudio import (
    MateriaPlanEstudioCreate,
    MateriaPlanEstudioUpdate,
)

from app.models.materia_plan_estudio import MateriaPlanEstudio


class MateriaPlanEstudioService:
    def __init__(self, db: AsyncSession):
        self.db = db
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
        
        await self._validar_relacion_materia_plan_unica(
            materia_catalogo_id=payload.materia_catalogo_id,
            plan_estudio_id=payload.plan_estudio_id,
        )

        return await self.repository.create(payload.model_dump())
    
    async def update_relacion(
        self,
        materia_plan_estudio_id: UUID,
        payload: MateriaPlanEstudioUpdate,
    ):
        relation = await self.get_relacion(materia_plan_estudio_id) 
        data = payload.model_dump(exclude_unset=True) 

        materia_catalogo_id = data.get(
            "materia_catalogo_id",
            relation.materia_catalogo_id,
        )

        plan_estudio_id = data.get(
            "plan_estudio_id",
            relation.plan_estudio_id,
        )

        await self._validar_relacion_materia_plan_unica(
            materia_catalogo_id=materia_catalogo_id,
            plan_estudio_id=plan_estudio_id,
            materia_plan_estudio_id_excluir=relation.materia_plan_estudio_id,
        )

        return await self.repository.update(relation, data)

    async def deactivate_relacion(self, materia_plan_estudio_id: UUID):
        relation = await self.get_relacion(materia_plan_estudio_id)

        return await self.repository.deactivate(relation)
    
    async def _validar_relacion_materia_plan_unica(
        self,
        materia_catalogo_id: UUID,
        plan_estudio_id: UUID,
        materia_plan_estudio_id_excluir: UUID | None = None,
    ) -> None:
        stmt = select(MateriaPlanEstudio).where(
            MateriaPlanEstudio.materia_catalogo_id == materia_catalogo_id,
            MateriaPlanEstudio.plan_estudio_id == plan_estudio_id,
        )

        if materia_plan_estudio_id_excluir is not None:
            stmt = stmt.where(
                MateriaPlanEstudio.materia_plan_estudio_id
                != materia_plan_estudio_id_excluir
            )

        result = await self.db.execute(stmt)
        existente = result.scalars().first()

        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="La materia ya está relacionada con ese plan de estudio",
            )