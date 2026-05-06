from decimal import Decimal
from typing import List
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class CriterioPonderacionCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100)
    porcentaje: Decimal = Field(..., gt=0, le=100)
    orden: int = Field(default=1, ge=1)

    @field_validator("nombre")
    @classmethod
    def limpiar_nombre(cls, value: str) -> str:
        return value.strip()


class PonderacionesCreate(BaseModel):
    criterios: List[CriterioPonderacionCreate] = Field(..., min_length=1)


class CriterioPonderacionResponse(BaseModel):
    id: UUID
    materia_id: UUID
    nombre: str
    porcentaje: Decimal
    orden: int


class PonderacionesResponse(BaseModel):
    materia_id: UUID
    total: Decimal
    criterios: List[CriterioPonderacionResponse]