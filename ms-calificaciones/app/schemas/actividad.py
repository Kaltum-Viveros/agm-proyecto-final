from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class ActividadCreate(BaseModel):
    materia_id: UUID
    ponderacion_id: UUID
    nombre: str = Field(..., min_length=1, max_length=150)
    descripcion: Optional[str] = Field(default=None, max_length=500)
    valor_maximo: Decimal = Field(default=Decimal("10"), gt=0, le=100)
    fecha_aplicacion: Optional[date] = None

    @field_validator("nombre")
    @classmethod
    def limpiar_nombre(cls, value: str) -> str:
        return value.strip()


class ActividadUpdate(BaseModel):
    ponderacion_id: Optional[UUID] = None
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=150)
    descripcion: Optional[str] = Field(default=None, max_length=500)
    valor_maximo: Optional[Decimal] = Field(default=None, gt=0, le=100)
    fecha_aplicacion: Optional[date] = None
    estado: Optional[str] = Field(default=None, pattern="^(activa|cerrada|cancelada)$")

    @field_validator("nombre")
    @classmethod
    def limpiar_nombre(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        return value.strip()


class ActividadResponse(BaseModel):
    id: UUID
    materia_id: UUID
    ponderacion_id: UUID
    nombre: str
    descripcion: Optional[str]
    valor_maximo: Decimal
    fecha_aplicacion: Optional[date]
    estado: str