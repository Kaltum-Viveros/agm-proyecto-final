from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.repositories.materia_catalogo_repository import MateriaCatalogoRepository
from app.repositories.materia_ofertada_repository import MateriaOfertadaRepository
from app.repositories.periodo_repository import PeriodoRepository
from app.schemas.materia_ofertada import MateriaOfertadaCreate, MateriaOfertadaUpdate

from app.models.materia_ofertada import MateriaOfertada

from app.core.academic_rules import (
    MateriaOfertadaEstado,
    validar_estado_materia_ofertada,
)

class MateriaOfertadaService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = MateriaOfertadaRepository(db)
        self.periodo_repository = PeriodoRepository(db)
        self.materia_repository = MateriaCatalogoRepository(db)

    async def list_materias_ofertadas(
        self,
        periodo_id: UUID | None = None,
        materia_catalogo_id: UUID | None = None,
        docente_id: UUID | None = None,
        estado: str | None = None,
        nrc: str | None = None,
        page: int = 1,
        limit: int = 10,
    ):
        return await self.repository.list(
            periodo_id=periodo_id,
            materia_catalogo_id=materia_catalogo_id,
            docente_id=docente_id,
            estado=estado,
            nrc=nrc,
            page=page,
            limit=limit,
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

        validar_estado_materia_ofertada(payload.estado)

        await self._validar_nrc_unico_en_periodo(
            periodo_id=payload.periodo_id,
            nrc=payload.nrc,
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

        await self._validar_nrc_unico_en_periodo(
            periodo_id=periodo_id,
            nrc=nrc,
            materia_ofertada_id_excluir=materia_ofertada.materia_ofertada_id,
        )

        if "estado" in data:
            validar_estado_materia_ofertada(data["estado"])

        return await self.repository.update(materia_ofertada, data)

    async def deactivate_materia_ofertada(self, materia_ofertada_id: UUID):
        materia_ofertada = await self.get_materia_ofertada(materia_ofertada_id)

        return await self.repository.deactivate(materia_ofertada)
    
    async def cambiar_estado_materia_ofertada(
        self,
        materia_ofertada_id: UUID,
        nuevo_estado: str,
    ):
        validar_estado_materia_ofertada(nuevo_estado)

        materia = await self.get_materia_ofertada(materia_ofertada_id)

        return await self.repository.update(
            materia,
            {"estado": nuevo_estado},
        )


    async def activar_materia_ofertada(self, materia_ofertada_id: UUID):
        return await self.cambiar_estado_materia_ofertada(
            materia_ofertada_id,
            MateriaOfertadaEstado.ACTIVA.value,
        )


    async def cerrar_materia_ofertada(self, materia_ofertada_id: UUID):
        return await self.cambiar_estado_materia_ofertada(
            materia_ofertada_id,
            MateriaOfertadaEstado.CERRADA.value,
        )


    async def cancelar_materia_ofertada(self, materia_ofertada_id: UUID):
        return await self.cambiar_estado_materia_ofertada(
            materia_ofertada_id,
            MateriaOfertadaEstado.CANCELADA.value,
        )
    
    async def asignar_docente_materia_ofertada(
        self,
        materia_ofertada_id: UUID,
        docente_id: UUID,
        docente_nombre: str | None = None,
    ):
        materia = await self.get_materia_ofertada(materia_ofertada_id)

        if materia.estado in {
            MateriaOfertadaEstado.CERRADA.value,
            MateriaOfertadaEstado.CANCELADA.value,
        }:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede asignar docente a una materia cerrada o cancelada",
            )

        data = {"docente_id": docente_id}

        if docente_nombre is not None:
            data["docente_nombre"] = docente_nombre

        return await self.repository.update(materia, data)
    
    async def _validar_nrc_unico_en_periodo(
        self,
        periodo_id,
        nrc: str,
        materia_ofertada_id_excluir: UUID | None = None,
    ) -> None:
        stmt = select(MateriaOfertada).where(
            MateriaOfertada.periodo_id == periodo_id,
            MateriaOfertada.nrc == nrc,
        )

        if materia_ofertada_id_excluir is not None:
            stmt = stmt.where(
                MateriaOfertada.materia_ofertada_id != materia_ofertada_id_excluir
            )

        result = await self.db.execute(stmt)
        existente = result.scalars().first()

        if existente:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe una materia ofertada con ese NRC en el mismo periodo",
            )