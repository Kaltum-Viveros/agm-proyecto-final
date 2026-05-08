from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.materia_catalogo_repository import MateriaCatalogoRepository
from app.repositories.materia_ofertada_repository import MateriaOfertadaRepository
from app.repositories.periodo_repository import PeriodoRepository
from app.schemas.materia_ofertada import MateriaOfertadaCreate, MateriaOfertadaUpdate


class MateriaOfertadaService:
    def __init__(self, db: AsyncSession):
        self.repository = MateriaOfertadaRepository(db)
        self.periodo_repository = PeriodoRepository(db)
        self.materia_repository = MateriaCatalogoRepository(db)

    async def list_materias_ofertadas(
        self,
        periodo_id: UUID | None = None,
        materia_catalogo_id: UUID | None = None,
        docente_id: UUID | None = None,
        estado: str | None = None,
    ):
        return await self.repository.list(
            periodo_id=periodo_id,
            materia_catalogo_id=materia_catalogo_id,
            docente_id=docente_id,
            estado=estado,
        )

    async def get_materia_ofertada(self, materia_ofertada_id: UUID):
        materia_ofertada = await self.repository.get_by_id(materia_ofertada_id)

        if materia_ofertada is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Materia ofertada no encontrada",
            )

        return materia_ofertada

    async def create_materia_ofertada(self, payload: MateriaOfertadaCreate):
        periodo = await self.periodo_repository.get_by_id(payload.periodo_id)

        if periodo is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Periodo no encontrado",
            )

        materia = await self.materia_repository.get_by_id(payload.materia_catalogo_id)

        if materia is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Materia del catálogo no encontrada",
            )

        existing = await self.repository.get_by_periodo_and_nrc(
            periodo_id=payload.periodo_id,
            nrc=payload.nrc,
        )

        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe una materia ofertada con ese NRC en el periodo",
            )

        return await self.repository.create(payload.model_dump())

    async def update_materia_ofertada(
        self,
        materia_ofertada_id: UUID,
        payload: MateriaOfertadaUpdate,
    ):
        materia_ofertada = await self.get_materia_ofertada(materia_ofertada_id)
        data = payload.model_dump(exclude_unset=True)

        periodo_id = data.get("periodo_id", materia_ofertada.periodo_id)
        nrc = data.get("nrc", materia_ofertada.nrc)

        if "periodo_id" in data:
            periodo = await self.periodo_repository.get_by_id(data["periodo_id"])

            if periodo is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Periodo no encontrado",
                )

        if "materia_catalogo_id" in data:
            materia = await self.materia_repository.get_by_id(
                data["materia_catalogo_id"]
            )

            if materia is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Materia del catálogo no encontrada",
                )

        existing = await self.repository.get_by_periodo_and_nrc(
            periodo_id=periodo_id,
            nrc=nrc,
        )

        if (
            existing is not None
            and existing.materia_ofertada_id != materia_ofertada_id
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe una materia ofertada con ese NRC en el periodo",
            )

        return await self.repository.update(materia_ofertada, data)

    async def deactivate_materia_ofertada(self, materia_ofertada_id: UUID):
        materia_ofertada = await self.get_materia_ofertada(materia_ofertada_id)

        return await self.repository.deactivate(materia_ofertada)