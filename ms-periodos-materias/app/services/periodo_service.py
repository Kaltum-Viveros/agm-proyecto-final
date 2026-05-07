from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.periodo_repository import PeriodoRepository
from app.schemas.periodo import PeriodoCreate, PeriodoUpdate


class PeriodoService:

    def __init__(self, db: AsyncSession):
        self.repository = PeriodoRepository(db)

    #funcion para listar los periodos, con un filtro opcional para mostrar solo los activos o inactivos
    async def list_periodos(self, activo: bool | None = None):
        return await self.repository.list(activo=activo)
    
    # funcion para obtener un periodo por su id, si no se encuentra se lanza una excepcion 404
    async def get_periodo(self, periodo_id: UUID):
        periodo = await self.repository.get_by_id(periodo_id)

        if periodo is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Periodo no encontrado",
            )

        return periodo

    # funcion para crear un periodo, se valida que la fecha de inicio no sea mayor a la fecha de fin, 
    # si el periodo se crea como activo se desactivan todos los periodos activos
    async def create_periodo(self, payload: PeriodoCreate):
        if payload.fecha_inicio > payload.fecha_fin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La fecha de inicio no puede ser mayor a la fecha de fin",
            )

        data = payload.model_dump()

        if data.get("activo") is True:
            await self.repository.deactivate_all_active()

        return await self.repository.create(data)

    # funcion para actualizar un periodo, se valida que la fecha de inicio no sea mayor a la fecha de fin,
    async def update_periodo(self, periodo_id: UUID, payload: PeriodoUpdate):
        periodo = await self.get_periodo(periodo_id)

        data = payload.model_dump(exclude_unset=True)

        fecha_inicio = data.get("fecha_inicio", periodo.fecha_inicio)
        fecha_fin = data.get("fecha_fin", periodo.fecha_fin)

        if fecha_inicio > fecha_fin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La fecha de inicio no puede ser mayor a la fecha de fin",
            )

        if data.get("activo") is True:
            await self.repository.deactivate_all_active()

        return await self.repository.update(periodo, data)

    # funcion para desactivar un periodo, se valida que el periodo exista, si no se encuentra se lanza una excepcion 404
    async def deactivate_periodo(self, periodo_id: UUID):
        periodo = await self.get_periodo(periodo_id)

        return await self.repository.deactivate(periodo)