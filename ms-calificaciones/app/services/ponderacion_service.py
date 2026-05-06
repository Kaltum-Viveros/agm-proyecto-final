from decimal import Decimal
from uuid import UUID, uuid4

from fastapi import HTTPException, status

from app.repositories.ponderacion_memory_repository import PonderacionMemoryRepository
from app.schemas.ponderacion import PonderacionesCreate


class PonderacionService:
    def __init__(self, repository: PonderacionMemoryRepository):
        self.repository = repository

    def crear_o_reemplazar(self, materia_id: UUID, payload: PonderacionesCreate) -> dict:
        self._validar_suma_100(payload)
        self._validar_nombres_unicos(payload)

        criterios = [
            {
                "id": uuid4(),
                "materia_id": materia_id,
                "nombre": criterio.nombre,
                "porcentaje": criterio.porcentaje,
                "orden": criterio.orden,
            }
            for criterio in payload.criterios
        ]

        criterios_ordenados = sorted(criterios, key=lambda item: item["orden"])
        self.repository.replace_by_materia(materia_id, criterios_ordenados)

        return {
            "materia_id": materia_id,
            "total": sum(item["porcentaje"] for item in criterios_ordenados),
            "criterios": criterios_ordenados,
        }

    def obtener_por_materia(self, materia_id: UUID) -> dict:
        criterios = self.repository.get_by_materia(materia_id)

        if not criterios:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No existen ponderaciones configuradas para esta materia",
            )

        return {
            "materia_id": materia_id,
            "total": sum(item["porcentaje"] for item in criterios),
            "criterios": criterios,
        }

    def _validar_suma_100(self, payload: PonderacionesCreate) -> None:
        total = sum(criterio.porcentaje for criterio in payload.criterios)

        if total != Decimal("100"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La suma de las ponderaciones debe ser exactamente 100",
            )

    def _validar_nombres_unicos(self, payload: PonderacionesCreate) -> None:
        nombres = [criterio.nombre.lower() for criterio in payload.criterios]

        if len(nombres) != len(set(nombres)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se permiten criterios de ponderación con nombres repetidos",
            )