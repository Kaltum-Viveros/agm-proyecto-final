from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.materia_horario_repository import MateriaHorarioRepository
from app.repositories.materia_ofertada_repository import MateriaOfertadaRepository
from app.schemas.materia_horario import MateriaHorarioCreate, MateriaHorarioUpdate


class MateriaHorarioService:
    def __init__(self, db: AsyncSession):
        self.repository = MateriaHorarioRepository(db)
        self.materia_ofertada_repository = MateriaOfertadaRepository(db)

    async def list_materia_horarios(
        self,
        materia_ofertada_id: UUID | None = None,
        dia: str | None = None,
        page: int = 1,
        limit: int = 10,
    ):
        return await self.repository.list(
            materia_ofertada_id=materia_ofertada_id,
            dia=dia,
            page=page,
            limit=limit,
        )

    async def get_horario(self, materia_horario_id: UUID):
        horario = await self.repository.get_by_id(materia_horario_id)

        if horario is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Horario de materia no encontrado",
            )

        return horario

    async def create_horario(self, payload: MateriaHorarioCreate):
        materia_ofertada = await self.materia_ofertada_repository.get_by_id(
            payload.materia_ofertada_id
        )

        if materia_ofertada is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Materia ofertada no encontrada",
            )

        return await self.repository.create(payload.model_dump())

    async def update_horario(
        self,
        materia_horario_id: UUID,
        payload: MateriaHorarioUpdate,
    ):
        horario = await self.get_horario(materia_horario_id)
        data = payload.model_dump(exclude_unset=True)

        hora_inicio = data.get("hora_inicio", horario.hora_inicio)
        hora_fin = data.get("hora_fin", horario.hora_fin)

        if hora_inicio >= hora_fin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La hora de inicio debe ser menor que la hora de fin",
            )

        return await self.repository.update(horario, data)

    async def delete_horario(self, materia_horario_id: UUID):
        horario = await self.get_horario(materia_horario_id)

        await self.repository.delete(horario)