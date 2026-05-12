from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.repositories.periodo_repository import PeriodoRepository
from app.schemas.periodo import PeriodoCreate, PeriodoUpdate

from app.core.academic_rules import validar_rango_fechas
from app.models.periodo import Periodo

class PeriodoService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = PeriodoRepository(db)

    async def _validar_unico_periodo_activo(
        self,
        periodo_id_excluir: UUID | None = None,
    ) -> None:
        stmt = select(Periodo).where(Periodo.activo.is_(True))

        if periodo_id_excluir is not None:
            stmt = stmt.where(Periodo.periodo_id != periodo_id_excluir)

        result = await self.db.execute(stmt)
        periodo_activo = result.scalars().first()

        if periodo_activo:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ya existe un periodo activo. Desactiva el periodo actual antes de activar otro.",
            )

    #funcion para listar los periodos, con un filtro opcional para mostrar solo los activos o inactivos
    async def list_periodos(
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
    
    # funcion para obtener un periodo por su id, si no se encuentra se lanza una excepcion 404
    async def get_periodo(self, periodo_id: UUID):
        periodo = await self.repository.get_by_id(periodo_id)

        if periodo is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Periodo no encontrado",
            )

        return periodo

    # si el periodo se crea como activo, se valida que no exista otro periodo activo
    async def create_periodo(self, payload: PeriodoCreate):
        validar_rango_fechas(payload.fecha_inicio, payload.fecha_fin)

        data = payload.model_dump()

        if data.get("activo") is True:
            await self._validar_unico_periodo_activo()

        return await self.repository.create(data)

    # funcion para actualizar un periodo, se valida que la fecha de inicio no sea mayor a la fecha de fin,
    async def update_periodo(self, periodo_id: UUID, payload: PeriodoUpdate):
        periodo = await self.get_periodo(periodo_id)

        data = payload.model_dump(exclude_unset=True)

        fecha_inicio = data.get("fecha_inicio", periodo.fecha_inicio)
        fecha_fin = data.get("fecha_fin", periodo.fecha_fin)

        validar_rango_fechas(fecha_inicio, fecha_fin)

        if data.get("activo") is True:
            await self._validar_unico_periodo_activo(
                periodo_id_excluir=periodo.periodo_id
            )

        return await self.repository.update(periodo, data)

    # funcion para desactivar un periodo, se valida que el periodo exista, si no se encuentra se lanza una excepcion 404
    async def deactivate_periodo(self, periodo_id: UUID):
        periodo = await self.get_periodo(periodo_id)

        return await self.repository.deactivate(periodo)
    
    # funcion para activar un periodo, se valida que el periodo exista, si no se encuentra se lanza una excepcion 404, 
    # si el periodo ya esta activo se retorna el mismo periodo, si no se valida que no exista otro periodo activo 
    # antes de activar el nuevo periodo
    async def activar_periodo(self, periodo_id: UUID):
        periodo = await self.get_periodo(periodo_id)

        if periodo.activo is True:
            return periodo

        await self._validar_unico_periodo_activo(
            periodo_id_excluir=periodo.periodo_id
        )

        return await self.repository.update(periodo, {"activo": True})